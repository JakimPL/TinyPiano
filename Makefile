CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99
LDFLAGS = -lm

all: extract_weights model test_synth
model: src/main.c src/model.c src/weights.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

test_synth: src/test_synth.c src/synth.c src/model.c src/weights.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

extract_weights: python/extract_weights.py
	python3 python/extract_weights.py

clean:
	rm -f model test_synth

.PHONY: all clean model extract_weights test_synth
