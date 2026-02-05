public class ForLoop {
    public static void main(String[] args) {
        long s = 0;
        for (int i = 0; i < 10_000_000; i++) {
            s += i;
        }
    }
}
