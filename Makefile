CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99
LDFLAGS = -lm

all: extract_weights model
model: src/main.c src/model.c src/weights.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

extract_weights: python/extract_weights.py
	python3 python/extract_weights.py

clean:
	rm -f model

.PHONY: all clean model extract_weights
