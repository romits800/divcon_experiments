
CFLAGS		+= -ffreestanding -march=mips32r2 -msoft-float -Wa,-msoft-float
ASFLAGS		+= -msoft-float

ASFILES         = $(wildcard *.s)
OBJFILES        = $(ASFILES:.s=.s.o)

all: $(OBJFILES)

envcheck:
	@echo "$(TARGET)" | grep mcb32 > /dev/null || (\
		echo ""; \
		echo " **************************************************************"; \
		echo " * Make sure you have sourced the cross compiling environment *"; \
		echo " * Do this by issuing:                                        *"; \
		echo " * . /path/to/crosscompiler/environment                       *"; \
		echo " **************************************************************"; \
		echo ""; \
		exit 1)


%.s.o: %.s envcheck 
	$(CC) $(CFLAGS) $(ASFLAGS) -c -MD -o $@ $<

#@cp $*.s.d $(df).s.P; sed -e 's/#.*//' -e 's/^[^:]*: *//' -e 's/ *\\$$//' -e '/^$$/ d' -e 's/$$/ :/' < $*.s.d >> $(df).s.P; $(RM) $*.s.d
clean:
	${RM} *.o



