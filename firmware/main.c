#include <xc.h>
#include <stdint.h>
#include "weights.h"

#pragma config OSC = INTIO67, WDT = OFF, LVP = OFF, PBADEN = OFF
#define _XTAL_FREQ 4000000

uint8_t img[IN_DIM];
int8_t  hidden[HID_DIM];

void uart_init(void) {
    OSCCONbits.IRCF = 0b110; // 4 MHz internal oscillator
    TRISCbits.TRISC6 = 0;    // TX output
    TRISCbits.TRISC7 = 1;    // RX input
    TXSTA = 0x24;            // TXEN=1, BRGH=1
    RCSTA = 0x90;            // SPEN=1, CREN=1
    SPBRG = 25;              // 9600 bps @ 4 MHz
}

uint8_t uart_rx(void) {
    if (RCSTAbits.OERR) {
        RCSTAbits.CREN = 0;
        RCSTAbits.CREN = 1;
    }
    while (!PIR1bits.RCIF);
    return RCREG;
}

void uart_tx(uint8_t data) {
    while (!TXSTAbits.TRMT);
    TXREG = data;
}

uint8_t mlp_predict(const uint8_t *x) {
    for (uint8_t h = 0; h < HID_DIM; h++) {
        int32_t acc = (int32_t)B1[h] * 16;
        for (uint8_t i = 0; i < IN_DIM; i++) {
            if (x[i]) {
                acc += (int16_t)x[i] * (int16_t)W1[h][i];
            }
        }
        if (acc < 0) acc = 0;
        int32_t val = acc >> L1_SHIFT;
        hidden[h] = (val > 127) ? 127 : (int8_t)val;
    }

    uint8_t best_cls = 0;
    int32_t best_score = -2147483647;
    for (uint8_t o = 0; o < OUT_DIM; o++) {
        int32_t acc = B2[o];
        for (uint8_t h = 0; h < HID_DIM; h++) {
            acc += (int32_t)hidden[h] * (int32_t)W2[o][h];
        }
        if (acc > best_score) {
            best_score = acc;
            best_cls = o;
        }
    }
    return best_cls;
}

void main(void) {
    uart_init();
    while (1) {
        if (uart_rx() == 0xAA) {
            for (uint8_t i = 0; i < IN_DIM; i++) {
                img[i] = uart_rx();
            }
            uint8_t pred = mlp_predict(img);
            uart_tx('0' + pred);
        }
    }
}
