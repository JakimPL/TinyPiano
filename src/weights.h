#pragma once

#define INPUT_SIZE 4
#define HIDDEN1_SIZE 16
#define HIDDEN2_SIZE 16
#define HIDDEN3_SIZE 8
#define OUTPUT_SIZE 1

extern unsigned char weights1_q[];
extern unsigned char biases1_q[];
extern unsigned char weights2_q[];
extern unsigned char biases2_q[];
extern unsigned char weights3_q[];
extern unsigned char biases3_q[];
extern unsigned char weights_out_q[];
extern unsigned char biases_out_q[];

extern float weights1_min, weights1_max;
extern float biases1_min, biases1_max;
extern float weights2_min, weights2_max;
extern float biases2_min, biases2_max;
extern float weights3_min, weights3_max;
extern float biases3_min, biases3_max;
extern float weights_out_min, weights_out_max;
extern float biases_out_min, biases_out_max;

float dequantize(unsigned char value, float min_val, float max_val);
