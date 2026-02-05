package main

import "math/rand"

func main() {
	r := rand.New(rand.NewSource(42))
	inside := 0
	n := 10_000_000
	for i := 0; i < n; i++ {
		x := r.Float64()
		y := r.Float64()
		if x*x+y*y <= 1.0 {
			inside++
		}
	}
}
