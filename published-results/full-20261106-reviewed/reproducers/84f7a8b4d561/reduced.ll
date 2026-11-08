
define <4 x i32> @load_v4i32_align8(ptr addrspace(2) %ptr) {
  %val = load <4 x i32>, ptr addrspace(2) %ptr, align 8
  ret <4 x i32> %val
}
