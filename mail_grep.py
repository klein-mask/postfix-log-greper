import sys
import subprocess
import json
from io import open
import os

class MailGrep:

    def __init__(self, input_file_path, address, grep_step=100):
        self.input_file_path = input_file_path
        self.address = address
        self.grep_step = grep_step
        self.data = {
            address: 0
        }

    def count(self):
        print('grep start')

        results = []
        try:
            cmd = ['zgrep', 'from=<' + self.address, self.input_file_path]
            results = subprocess.check_output(cmd).splitlines()
        except subprocess.CalledProcessError as e:
            print('address :: ' + self.address + ' no results')
            print(e)

        results = list(self.split_list(results, self.grep_step))
        loop_cnt = 0
        for res in results:
            try:
                cmd = self.make_cmd_from_results(res)
                r = subprocess.check_output(cmd).splitlines()
                r = set([x.decode().split(': ')[1] for x in r])

                self.data[self.address] += len(list(r))
            except subprocess.CalledProcessError as e:
                continue
            finally:
                loop_cnt += 1
                print('loopcnt :: ' + str(loop_cnt))

        print('grep end')

    def split_list(self, l, n):
        for idx in range(0, len(l), n):
            yield l[idx:idx + n]

    def make_cmd_from_results(self, results_split_100):
        conds = []
        for r in results_split_100:
            que_id = r.decode().split(': ')[1]
            conds.append(que_id + '.*status=sent')
        return ('zgrep -e ' + ' -e '.join(conds) + ' ' + self.input_file_path).split()

    def save(self):
        s = json.dumps(self.data)
        print(s)

if __name__ == '__main__':
    args = sys.argv

    if len(args) == 3:
        MG = MailGrep(args[1], args[2])
        MG.count()
        MG.save()
