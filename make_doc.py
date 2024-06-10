#!/usr/bin/env python3

import yaml
import subprocess
# from jinja2 import Environment, BaseLoader

import argparse
parser = argparse.ArgumentParser(description='play play_doc and render memaid')
parser.add_argument("-i", "--input", help = "cmd and doc playlist")
parser.add_argument("-o", "--output", help = "gitlab mermaid format")
parser.add_argument("--halt", action="store_true", help="inspect stdin")

args = parser.parse_args()

play_doc_book_file_name = "play_doc_cmd.yml"



if args.input:
    play_doc_book_file_name = args.input
else:
    print("ERROR play_doc_book_file_name is mandatory")
    exit(1)


if args.output:
    outfile = open(args.output, "w", encoding='utf-8')
    outfile.write("[[_TOC_]]\n")

with open(play_doc_book_file_name, 'r') as input_yaml:
    play_doc_book = yaml.safe_load(input_yaml)


for play_doc in play_doc_book:
    
    if 'stop' in play_doc:
        break
    
    # print(play_doc)
    if 'name' in play_doc:
        print(play_doc['name'])
        if args.output:
            outfile.write("  \n#### " + play_doc['name'] + '\n')
            
    if 'collapse' in play_doc:
        if args.output:
            outfile.write("<details>\n\n")
            max_length = 120
            start_str = "<summary>" + play_doc['collapse']
            end_str = "(⬇️ Click to expand)</summary>  \n\n"
            space_left = max_length - (len(start_str) + len(end_str))
            space_left = 0 if space_left < 0 else space_left
            format_string = "{0:.>" + str(space_left) + "}"
            outfile.write(start_str + format_string.format(end_str))
            
            
    if 'text' in play_doc:
        print(play_doc['text'])
        if args.output:
            outfile.write(play_doc['text'] + "\n" )
    
    if 'play_cmd' in play_doc and 'eval_cmd' in play_doc:
        print("ERROR play_cmd and eval_cmd options can't be used together")
        exit(1)
            
    if 'play_cmd' in play_doc or 'eval_cmd' in play_doc :
        box_as = ""
        is_play_cmd = True if 'play_cmd' in play_doc else False
        is_eval_cmd = True if 'eval_cmd' in play_doc else False
        cmd = play_doc['play_cmd'] if is_play_cmd else play_doc['eval_cmd']
        print("\ncmd was: \n" + cmd)
        
        if args.output:
            if is_play_cmd:
                out = "\ncommand: \n```" + "bash" + "\n" + cmd + "\n```\n"
                outfile.write(out)
            
        try:
            output = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True, timeout=3,
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            status = exc.returncode
            err = exc.output
            print(err)
            print("Status : FAIL", exc.returncode, exc.output)
            if args.output:
                box_as = ""
                if "box_as" in play_doc:
                    box_as = play_doc['box_as']
                out_err = "\n```" + box_as + "\n💥 Something was wrong with this report\n```\n"
                if is_play_cmd:
                    out_err = "output:\n" + out_err
                outfile.write(out_err)
                print(out_err)
            if args.halt:
                exit(1)
                
        else:
            # print("Output: \n{}\n".format(output))
            print(output)
            if args.output:
                box_as = ""
                if "box_as" in play_doc:
                    box_as = play_doc['box_as']
                out = "\n```" + box_as + "\n" + output + "\n```\n"
                if is_play_cmd:
                    out = "output:\n" + out
                outfile.write(out)
                
    if 'collapse' in play_doc:
        if args.output:
            outfile.write("</details>\n\n")

outfile.close()