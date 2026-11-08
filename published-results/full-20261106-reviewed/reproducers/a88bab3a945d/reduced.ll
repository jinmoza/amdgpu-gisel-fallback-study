
define <2 x half> @load_v2f16(ptr addrspace(2) %ptr) {
  %val = load <2 x half>, ptr addrspace(2) %ptr, align 4
  ret <2 x half> %val
}
