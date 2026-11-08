
define amdgpu_kernel void @ubsantrap_requires_queue_ptr() {
  call void @llvm.ubsantrap(i8 0)
  unreachable
}

; Function Attrs: cold noreturn nounwind memory(inaccessiblemem: write)
declare void @llvm.ubsantrap(i8 immarg) #0

attributes #0 = { cold noreturn nounwind memory(inaccessiblemem: write) }
