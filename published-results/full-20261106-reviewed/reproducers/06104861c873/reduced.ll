; ModuleID = '<bc file>'
source_filename = "<WORKSPACE>/results/full-20261106-reviewed/reproducers/06104861c873/original.ll"

define amdgpu_kernel void @buildvector_undefs() {
entry:
  %i1 = call <16 x i16> @llvm.vector.insert.v16i16.v2i16(<16 x i16> zeroinitializer, <2 x i16> zeroinitializer, i64 2)
  store <16 x i16> %i1, ptr addrspace(1) null, align 32
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <16 x i16> @llvm.vector.insert.v16i16.v2i16(<16 x i16>, <2 x i16>, i64 immarg) #0

attributes #0 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
