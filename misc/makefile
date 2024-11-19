filename = spellcards

neededfiles = resources/spell_full.tsv preamble/preamble.tex preamble/commands.tex din-a4.cfg


UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S), Linux)
	pdflatexcmd = pdflatex --shell-escape
	bibercmd = biber
	makeglossariescmd = makeglossaries
	pdfviewercmd = atril
endif

ifeq ($(UNAME_S), Darwin)
	pdflatexcmd = /usr/texbin/pdflatex --shell-escape
	bibercmd = /usr/texbin/biber
	makeglossaries = /usr/texbin/makeglossaries
	pdfviewercmd = open
endif


all: $(filename).tex $(neededfiles) latex clean
latex:
	$(pdflatexcmd) -halt-on-error -interaction=nonstopmode -shell-escape -synctex=1 -output-directory=output $(filename)

view:
	if [ -f "output/$(filename).pdf" ]; then \
		$(pdfviewercmd) "output/$(filename).pdf"; \
	else \
		$(MAKE) all ;\
		$(MAKE) view ;\
	fi
clean:
	git clean -fx
distclean:
	git checkout -f main
	$(MAKE) clean
