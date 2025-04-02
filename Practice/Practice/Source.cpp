#include <iostream>
using namespace std;



int display(int x) {
	if (x < 0) return 0;
	while (x > 0) {
		int y = x % 10;
		for (int i = 1; i <= y; i++) {
			cout << i;
		}
		x = x / 10;
		cout << endl;
	}
}




int main() {
	display(31415);
	return 0;
}