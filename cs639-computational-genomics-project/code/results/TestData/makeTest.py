import sys

def main():
	text = sys.stdin.readline().rstrip()
	out = ""
	for i in range(0,500000):
		out = out + text[i]

	f = open("500000.txt",'w')
	f.write(out)
	f.close()
main()