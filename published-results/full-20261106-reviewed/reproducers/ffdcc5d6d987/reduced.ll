
define <7 x i9> @load_elem_i9_access_7xi9() {
  %l = load <7 x i9>, ptr addrspace(5) null, align 1
  ret <7 x i9> %l
}
