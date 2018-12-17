# 

all: test01.out test02.out test03.out test04.out test05.out

test01.out:
	./test_diff23lib >test01.out
	@diff test01.out test01.out.good
	@echo "sucess $@"

test02.out:
	./test_imediff  -n file_a file_b -o test02.out
	@diff test02.out test02.out.good
	@echo "sucess $@"

test03.out:
	./test_imediff  -n file_a file_b file_c -o test03.out
	@diff test03.out test03.out.good
	@echo "sucess $@"

test04.out:
	./test_initialize -n file_a file_b file_c > test04.out
	@diff test04.out test04.out.good
	@echo "sucess $@"


test05.out:
	./test_macrotrans -C alternative_imediff.conf > test05.out 
	@diff test05.out test05.out.good
	@echo "sucess $@"

clean:
	-rm -rf *.out
