
.global ex2
.set noreorder

ex2:
	slt $t1, $a0, $0
	bzeq $t1, if1
	nop
	add $v0, $a0, $0
	jr $ra
	nop
if1: 
	sub $v0, $0, $a0
	jr $ra
	nop
