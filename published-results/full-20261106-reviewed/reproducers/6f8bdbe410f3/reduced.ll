
define <2 x ptr addrspace(2)> @load_v2p2(ptr addrspace(2) %ptr) {
  %val = load <2 x ptr addrspace(2)>, ptr addrspace(2) %ptr, align 8
  ret <2 x ptr addrspace(2)> %val
}
