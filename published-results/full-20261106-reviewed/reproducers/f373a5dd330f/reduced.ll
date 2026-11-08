
define <2 x i16> @atomic_load_v2i16(ptr addrspace(2) %ptr) {
  %val = load <2 x i16>, ptr addrspace(2) %ptr, align 4
  ret <2 x i16> %val
}
