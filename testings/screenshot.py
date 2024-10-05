#!/usr/bin/env python3


from html2image import Html2Image

import argparse, ast

parser = argparse.ArgumentParser(description='Render image from html')
parser.add_argument("-i", "--input", help = "html in put")
parser.add_argument("-o", "--output", help = "output png image")
parser.add_argument("-s", "--size", help = "output png image")


args = parser.parse_args()


if not args.input or not args.output:
    args = parser.parse_args(['--help'])

image_size = (500, 100)
if args.size:
    image_size = ast.literal_eval(args.size)
    


hti = Html2Image()
hti = Html2Image(size=image_size)


# hti.screenshot(url='https://www.python.org', save_as='python_org.png')
hti.screenshot(html_file=args.input, save_as=args.output)
