#!/usr/bin/env python3
"""Validate review records and calculate scores; Python 3 standard library only."""
import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

RULE_FILE = Path(__file__).resolve().parents[1] / 'references' / 'rubric.json'


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError('Non-finite JSON number: ' + value)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'),
                      object_pairs_hook=unique_keys, parse_constant=invalid_constant)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def rounded(value):
    return float(value.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


def validate_rule(rule):
    ids = []
    for dimension in rule['dimensions']:
        criteria = dimension['criteria']
        require(sum(c['max_score'] for c in criteria) == dimension['max_score'],
                'Dimension weights do not add up')
        for criterion in criteria:
            require(type(criterion['max_score']) is int and criterion['max_score'] > 0,
                    'Criterion weight must be a positive integer')
            ids.append(criterion['id'])
    require(len(ids) == len(set(ids)) == 14, 'Rule must have fourteen unique criteria')
    require(sum(d['max_score'] for d in rule['dimensions']) == rule['total'] == 100,
            'Rule weights must total 100')
    return ids


def template(rule):
    return {
        'metadata': {k: '未提供' for k in ['team_name', 'submission_version',
                     'scoring_time', 'platform_version', 'model_config']},
        'material_status': 'pending',
        'materials': [{'id': 'm1', 'file': '未提供', 'status': 'unreadable', 'critical': True}],
        'ratings': {c['id']: {'level': None, 'reason': '', 'evidence': []}
                    for d in rule['dimensions'] for c in d['criteria']}
    }


def calculate(data, rule, event_points=None, official=False):
    expected = validate_rule(rule)
    require(isinstance(data, dict), 'Input must be a JSON object')
    require(isinstance(data.get('metadata'), dict), 'metadata must be an object')
    require(data.get('material_status') in ['complete', 'pending'],
            'material_status must be complete or pending')
    metadata = dict(data['metadata'])
    for key in ['team_name', 'submission_version', 'scoring_time', 'platform_version', 'model_config']:
        require(nonempty(metadata.get(key)), 'Missing metadata: ' + key)
    require(isinstance(data.get('materials'), list) and data['materials'],
            'materials must be a nonempty array')
    sources = {}
    for material in data['materials']:
        require(isinstance(material, dict), 'Invalid material entry')
        mid = material.get('id')
        require(nonempty(mid) and mid not in sources, 'Missing or duplicate material id')
        require(nonempty(material.get('file')), 'Material must have a file or source name')
        require(material.get('status') in ['readable', 'unreadable'], 'Invalid material status')
        require(type(material.get('critical')) is bool, 'critical must be a boolean')
        sources[mid] = material
    if event_points is not None:
        event_points = Decimal(str(event_points))
        require(event_points.is_finite() and Decimal('0') < event_points <= Decimal('20'),
                'event-points must be finite, greater than zero and no more than 20')
    result = {'rule_version': rule['rule_version'], 'scope': rule['scope'],
              'assessment_use': 'organizer_review' if official else 'trial',
              'metadata': metadata, 'materials': data['materials'],
              'event_points_max': None if event_points is None else float(event_points),
              'rounding': 'ROUND_HALF_UP to one decimal',
              'status': 'scored', 'raw_score': None, 'score_100': None,
              'event_score_raw': None, 'event_score_preview': None, 'dimensions': []}
    blocked = [m['id'] for m in sources.values() if m['critical'] and m['status'] == 'unreadable']
    if data['material_status'] == 'pending' or blocked:
        result['status'] = 'pending'
        result['pending_reason'] = {'declared_pending': data['material_status'] == 'pending',
                                    'critical_unreadable_materials': blocked}
        return result
    ratings = data.get('ratings')
    require(isinstance(ratings, dict) and set(ratings) == set(expected),
            'ratings must contain exactly the fourteen rule criterion ids')
    total = Decimal('0')
    for dimension in rule['dimensions']:
        subtotal = Decimal('0')
        entries = []
        for criterion in dimension['criteria']:
            rating = ratings[criterion['id']]
            require(isinstance(rating, dict), 'Invalid rating: ' + criterion['id'])
            level = rating.get('level')
            require(type(level) is int and 0 <= level <= 4, 'Level must be an integer from 0 to 4')
            require(nonempty(rating.get('reason')), 'Each rating needs a reason')
            evidence = rating.get('evidence')
            require(isinstance(evidence, list) and evidence, 'Each rating needs evidence')
            for item in evidence:
                require(isinstance(item, dict), 'Invalid evidence entry')
                mid = item.get('material_id')
                require(isinstance(mid, str) and mid in sources and sources[mid]['status'] == 'readable',
                        'Evidence must refer to a readable listed material')
                require(nonempty(item.get('locator')) and nonempty(item.get('finding')),
                        'Evidence requires a locator and finding')
            score = Decimal(criterion['max_score']) * Decimal(level) / Decimal('4')
            subtotal += score
            entries.append({'id': criterion['id'], 'name': criterion['name'],
                            'max_score': criterion['max_score'], 'anchor': criterion['anchor'],
                            'level': level, 'raw_score': float(score),
                            'reason': rating['reason'], 'evidence': evidence})
        result['dimensions'].append({'id': dimension['id'], 'name': dimension['name'],
                                      'max_score': dimension['max_score'],
                                      'raw_score': float(subtotal), 'criteria': entries})
        total += subtotal
    result['raw_score'] = float(total)
    result['score_100'] = rounded(total)
    if event_points is not None:
        scaled = total / Decimal('100') * event_points
        result['event_score_raw'] = float(scaled)
        result['event_score_preview'] = rounded(scaled)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?', help='UTF-8 review JSON')
    parser.add_argument('--template', action='store_true', help='Print an unfilled review template')
    parser.add_argument('--event-points', help='Trusted organizer allocation for this task, at most 20')
    parser.add_argument('--official', action='store_true', help='Mark organizer use; does not verify authority')
    parser.add_argument('--output', help='New output JSON file; existing files are not overwritten')
    args = parser.parse_args()
    try:
        rule = read_json(RULE_FILE)
        validate_rule(rule)
        require(not (args.template and args.input), 'Use either --template or an input file')
        require(args.template or args.input, 'Provide an input file or --template')
        result = template(rule) if args.template else calculate(read_json(args.input), rule, args.event_points, args.official)
        content = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        if args.output:
            with Path(args.output).open('x', encoding='utf-8') as stream:
                stream.write(content)
        else:
            sys.stdout.write(content)
        return 0
    except (ValueError, TypeError, KeyError, OSError, ArithmeticError) as exc:
        sys.stderr.write('ERROR: ' + str(exc) + '\n')
        return 2


if __name__ == '__main__':
    sys.exit(main())
