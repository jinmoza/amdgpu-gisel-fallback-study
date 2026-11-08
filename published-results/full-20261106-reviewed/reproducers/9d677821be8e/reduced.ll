
define <3 x bfloat> @load_v3bf16(ptr addrspace(2) %ptr) {
  %val = load <3 x bfloat>, ptr addrspace(2) %ptr, align 8
  ret <3 x bfloat> %val
}
