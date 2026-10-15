.PHONY: all data model places page shots clean
all: data model page
data:
	bash scripts/fetch_model.sh
model:
	mkdir -p build && python3 scripts/reconstruct.py data/MERDITH2021 build/model.json
places:
	python3 scripts/gazetteer.py
page:
	python3 scripts/build.py
shots:
	python3 scripts/screenshot.py
clean:
	rm -f build/*.preview.html build/earth-4k.jpg
