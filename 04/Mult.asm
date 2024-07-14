// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

//// Replace this comment with your code.

// *i = 0
@i
M=0

// *R2 = 0
@R2
M=0

(LOOP)
    // D = *R1
    @R1
    D=M

    // D = D - *i
    @i
    D=D-M

    // if D = 0, GOTO END
    @END
    D;JEQ

    // D = *R0
    @R0
    D=M

    // *R2 = D + *R2 = *R0 + *R2
    @R2
    M=D+M

    // D = 1
    @1
    D=A

    // *i = D + *i = 1 + *i
    @i
    M=D+M

    @LOOP
    0;JMP

(END)
    @END
    0;JMP

