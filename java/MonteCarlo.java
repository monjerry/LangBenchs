import java.util.Random;

public class MonteCarlo {
    public static void main(String[] args) {
        Random rng = new Random(42);
        int inside = 0;
        int n = 10_000_000;
        for (int i = 0; i < n; i++) {
            double x = rng.nextDouble();
            double y = rng.nextDouble();
            if (x * x + y * y <= 1.0) inside++;
        }
    }
}
