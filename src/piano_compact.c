#include <stdio.h>
#include <math.h>

// Compact piano harmonics neural network model
// Architecture: 4 -> 8 -> 8 -> 4 -> 1 with SiLU activation

// SiLU activation: x * sigmoid(x)
float silu(float x) { return x / (1.0f + expf(-x)); }

// Embedded model weights (from trained PyTorch model)
static float w1[] = {-2.09316516f, -1.43079710f, -1.29498386f, -0.05881727f, 1.79933953f, 0.04013823f, 1.54859054f, 0.66007185f, 
    -0.35424069f, 0.20324609f, 1.92994249f, 0.34582090f, 0.36931449f, 0.93159723f, -1.80349684f, 0.69984466f, 
    -1.74909854f, 0.12884228f, 0.01581155f, 0.85631216f, 0.60396791f, 0.53168601f, 3.97497034f, 0.47461030f, 
    1.09487212f, -0.31953043f, 1.07259381f, 0.47504169f, 0.62364024f, -0.43365508f, 0.46448421f, 0.14089498f};

static float b1[] = {1.11608028f, -0.28256902f, 0.95281458f, 1.14453685f, 0.96012980f, 0.02843913f, 0.71194404f, 1.27347505f};

static float w2[] = {-2.81435776f, -2.20845819f, 0.71511692f, 0.11667145f, 1.66500568f, 0.24216947f, -1.02269864f, -0.14472079f, 
    1.90842104f, 0.02481720f, -0.22068590f, -0.63903946f, 0.62857872f, -0.12289757f, -0.46261254f, -0.44045642f, 
    1.13736391f, 0.22760388f, 0.44835392f, 0.09814782f, -0.83320153f, -0.22175658f, 0.55373174f, 0.92866361f, 
    2.16354680f, -0.49548608f, -0.57473290f, -1.14448762f, 1.44584608f, -0.41098613f, 0.42950106f, -0.03957656f, 
    -3.37893558f, -1.71634269f, -0.25681531f, 0.93743539f, 1.72348666f, -1.40868175f, -0.62138331f, 0.00412035f, 
    1.39531326f, -0.13822936f, 0.56472754f, 0.21714863f, -0.28162831f, 0.28251272f, 0.75062907f, 0.86219555f, 
    0.74221689f, 0.35093093f, 0.64415181f, -0.20691113f, -0.23840953f, 0.02362772f, 0.71537286f, 0.46022895f, 
    -0.29547310f, -0.11674355f, 0.50104362f, 0.35605940f, -1.16282940f, 0.38088879f, 0.12538572f, 0.49788058f};

static float b2[] = {0.90745878f, -0.27056691f, 0.97890466f, -0.87176430f, 1.44071269f, 0.46699560f, 0.67943835f, 0.73488837f};

static float w3[] = {-0.06958607f, -1.24924409f, 0.53410387f, -1.53071654f, -0.00067429f, 0.50945127f, 0.36035204f, 0.23790587f, 
    -0.79188609f, -0.68681997f, 0.48218569f, -2.27809906f, 0.25128087f, 0.28316751f, 0.19183828f, -0.10106967f, 
    -0.39787582f, -1.12188363f, 0.35159457f, -1.93978071f, 0.30040053f, 0.44952655f, 0.35552385f, 0.24149604f, 
    -4.11042500f, -0.01547927f, -0.00208680f, 0.73187536f, -4.16671801f, -0.06500108f, -0.00985010f, 0.57544899f};

static float b3[] = {0.69261050f, 0.70203942f, 0.44852042f, 0.13995726f};

static float w4[] = {-0.80249029f, -0.53604174f, -0.34038734f, -1.94901061f};

static float b4[] = {0.19641364f};

// Compact forward pass
float piano_harmonics(float pitch, float velocity, float harmonic, float time) {
    float x[8], y[8], z[4];
    
    // Layer 1: 4->8
    for(int i=0; i<8; i++) {
        x[i] = silu(w1[i*4] * pitch + w1[i*4+1] * velocity + w1[i*4+2] * harmonic + w1[i*4+3] * time + b1[i]);
    }
    
    // Layer 2: 8->8
    for(int i=0; i<8; i++) {
        float sum = b2[i];
        for(int j=0; j<8; j++) sum += x[j] * w2[i*8+j];
        y[i] = silu(sum);
    }
    
    // Layer 3: 8->4
    for(int i=0; i<4; i++) {
        float sum = b3[i];
        for(int j=0; j<8; j++) sum += y[j] * w3[i*8+j];
        z[i] = silu(sum);
    }
    
    // Output: 4->1
    return w4[0] * z[0] + w4[1] * z[1] + w4[2] * z[2] + w4[3] * z[3] + b4[0];
}

// Demo
int main() {
    float test_cases[][4] = {
        {0.5f, 0.8f, 0.1f, 0.3f},  // Middle pitch, strong velocity
        {0.0f, 0.5f, 0.0f, 0.0f},  // Lowest pitch, medium velocity
        {1.0f, 1.0f, 1.0f, 1.0f},  // Maximum values
        {0.25f, 0.6f, 0.5f, 0.8f}, // Mixed values
    };
    
    printf("Piano Harmonics Neural Network Demo\n");
    printf("===================================\n");
    printf("Input: (pitch, velocity, harmonic, time) -> log_amplitude\n\n");
    
    for(int i = 0; i < 4; i++) {
        float log_amp = piano_harmonics(test_cases[i][0], test_cases[i][1], 
                                       test_cases[i][2], test_cases[i][3]);
        float amplitude = expf(log_amp);
        
        printf("(%.2f, %.2f, %.2f, %.2f) -> %.3f (amp: %.6f)\n",
               test_cases[i][0], test_cases[i][1], test_cases[i][2], test_cases[i][3],
               log_amp, amplitude);
    }
    
    return 0;
}
