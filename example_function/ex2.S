
.global ex2
.set noreorder

ex2:
	slt $t1, $a0, $0
	beq $t1, $0, if1
	nop
	add $v0, $a0, $0
	jr $ra
	nop
if1: 
	sub $v0, $0, $a0
	jr $ra
	nop
