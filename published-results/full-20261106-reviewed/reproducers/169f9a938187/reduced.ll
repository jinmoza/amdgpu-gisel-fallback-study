
define <3 x half> @load_v3f16(ptr addrspace(2) %ptr) {
  %val = load <3 x half>, ptr addrspace(2) %ptr, align 8
  ret <3 x half> %val
}
