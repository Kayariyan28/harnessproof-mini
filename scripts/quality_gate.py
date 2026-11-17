#!/usr/bin/env python3
import argparse
import json
from harnessproof.quality import gate_from_directory

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['pilot','publish'],default='pilot')
    parser.add_argument('--data-dir',default='data/processed')
    args=parser.parse_args()
    report=gate_from_directory(args.data_dir,args.mode)
    print(json.dumps(report,indent=2))
    if not report['passed']:raise SystemExit(2)

if __name__=='__main__':main()
