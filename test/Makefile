
#10-select_a.py
#10-select_b.py
#10-select_d.py

diff:
	echo select-a
	./10-select_a.py foo_a foo_b >foo-select_a
	-diff -u foo_a foo-select_a
	echo select-b
	./10-select_b.py foo_a foo_b >foo-select_b
	-diff -u foo_b foo-select_b
	echo select-d
	./10-select_d.py foo_a foo_b >foo-select_d
	echo diff -u foo_a foo-select_d
	-diff -u foo_a foo-select_d
	echo diff -u foo_b foo-select_d
	-diff -u foo_b foo-select_d

clean:
	rm foo-select_a foo-select_b foo-select_d
