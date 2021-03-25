// prints all primes < n, O(n log log n)
import java.util.Scanner;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] spf = new int[n];
        for (int i = 2; i < n; i++)
            spf[i] = i;
        for (int i = 2; i < n; i++) {
            if (spf[i] < i)
                continue;
            System.out.println(i);
            for (int j = 2 * i; j < n; j += i)
                if (spf[j] == j)
                    spf[j] = i;
        }
    }
};