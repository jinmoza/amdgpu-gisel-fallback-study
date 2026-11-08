
define <2 x bfloat> @load_v2bf16(ptr addrspace(2) %ptr) {
  %val = load <2 x bfloat>, ptr addrspace(2) %ptr, align 4
  ret <2 x bfloat> %val
}
