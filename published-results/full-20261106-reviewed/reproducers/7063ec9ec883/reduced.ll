
define <3 x i32> @load_v3i32_align16(ptr addrspace(2) %ptr) {
  %val = load <3 x i32>, ptr addrspace(2) %ptr, align 16
  ret <3 x i32> %val
}
