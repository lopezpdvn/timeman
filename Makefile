GITHUB_REMOTE	=	origin
GITHUB_PUSH_BRANCHS	=	master

.PHONY: help

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  push         Push main branches to GitHub"

push:
	git push $(GITHUB_REMOTE) $(GITHUB_PUSH_BRANCHS)
