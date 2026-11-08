"""Forward the current public text-file value to Metamoa without logging secrets."""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

SOURCE_URL = 'https://raw.githubusercontent.com/batlabresearch/metamoaAPI/main/metamoaAPI.txt'
DESTINATION_URL = 'https://metamoa.com/api/live/batlabresearch-github-io-mw4gjmx2'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the Authorization header to another destination.
        return None


def parse_count(text):
    text = text.strip()
    if not re.fullmatch(r'[0-9]{1,6}', text):
        raise ValueError('Source must contain only an integer from 0 to 100000.')
    count = int(text)
    if count > 100000:
        raise ValueError('Source count exceeds 100000.')
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='Validate source without sending.')
    args = parser.parse_args()
    opener = urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(SOURCE_URL, headers={'Cache-Control': 'no-cache', 'User-Agent': 'metamoa-count-sender/1.0'})
    with opener.open(request, timeout=30) as response:
        count = parse_count(response.read(1024).decode('utf-8'))
    if args.dry_run:
        print(f'Validated count={count}; no POST sent.')
        return
    key = os.environ.get('METAMOA_SPACE_KEY', '').strip()
    if not key or not key.startswith('mm_live_'):
        raise ValueError('Set the METAMOA_SPACE_KEY repository Actions secret.')
    request = urllib.request.Request(
        DESTINATION_URL,
        data=json.dumps({'count': count}).encode('utf-8'),
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'User-Agent': 'metamoa-count-sender/1.0'},
        method='POST',
    )
    try:
        with opener.open(request, timeout=30) as response:
            status = response.status
    except urllib.error.HTTPError as error:
        if error.code == 429:
            print('Skipped: Metamoa rate limit (HTTP 429). Next scheduled run will retry.')
            return
        detail = ''
        if error.headers.get('Content-Type', '').startswith('application/json'):
            try:
                body = json.loads(error.read(4096))
                detail = str(body.get('error', ''))[:200]
            except (ValueError, AttributeError):
                pass
        raise RuntimeError(f'Metamoa HTTP {error.code}: {detail}; no immediate retry.') from None
    if status != 204:
        raise RuntimeError(f'Unexpected Metamoa HTTP {status}.')
    print(f'Success: count={count}; HTTP 204.')
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as output:
            output.write(f'Metamoa accepted **{count}** (HTTP 204).\n')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Do not print request headers, environment variables, or response bodies.
        message = str(error)
        key = os.environ.get('METAMOA_SPACE_KEY', '').strip()
        if key:
            message = message.replace(key, '[REDACTED]')
        print(f'Failed: {message}', file=sys.stderr)
        sys.exit(1)
