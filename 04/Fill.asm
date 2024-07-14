// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.

// KEYBOARD > 0 ? FILL : CLEAR

(LOOP)
    // get keyboard value
    @KBD
    D=M

    // jmp to ON if D > 0
    @ON
    D;JGT

    // jmp to OFF otherwise
    @OFF
    0;JMP

(ON)
    // set -1
    @R0
    M=-1

    // draw
    @DRAW
    0;JMP

(OFF)
    // set 0
    @R0
    M=0

    // draw
    @DRAW
    0;JMP

(DRAW)
    // *R1 = 8191
    @8191
    D=A
    @R1
    M=D

    (NEXT)
        // *pos = *R1 
        @R1
        D=M
        @pos
        M=D
        // *pos = *screen + *pos
        @SCREEN
        D=A
        @pos
        M=D+M

        // *(screen[*pos]) = *R0
        @R0
        D=M
        @pos
        A=M
        M=D

        // *R1 = *R1 - 1
        @R1
        D=M-1
        M=D

        // if *R1 >= 0, go to NEXT
        @NEXT
        D;JGE

    @LOOP
    0;JMP


