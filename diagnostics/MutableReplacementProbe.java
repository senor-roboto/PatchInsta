import java.io.File;
import java.util.*;
import com.android.tools.smali.dexlib2.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.dexlib2.immutable.*;
import com.android.tools.smali.dexlib2.immutable.instruction.*;
import com.android.tools.smali.dexlib2.immutable.reference.*;
import com.android.tools.smali.dexlib2.writer.pool.DexPool;
import app.morphe.patcher.util.proxy.mutableTypes.*;
import app.crimera.patches.instagram.misc.reels.RoundedCardHookKt;
public class MutableReplacementProbe {
 public static void main(String[] args) throws Exception {
  String type="Lcom/instagram/ui/widget/roundedcornerlayout/RoundedCornerFrameLayout;", canvas="Landroid/graphics/Canvas;";
  File file=new File(args[0]);
  var body=new ImmutableMethodImplementation(3,List.of(new ImmutableInstruction3rc(Opcode.INVOKE_SUPER_RANGE,1,2,new ImmutableMethodReference("Landroid/view/ViewGroup;","dispatchDraw",List.of(canvas),"V")),new ImmutableInstruction10x(Opcode.RETURN_VOID)),List.of(),List.of());
  var method=new ImmutableMethod(type,"dispatchDraw",List.of(new ImmutableMethodParameter(canvas,Set.of(),null)),"V",AccessFlags.PROTECTED.getValue(),Set.of(),Set.of(),body);
  var owner=new ImmutableClassDef(type,AccessFlags.PUBLIC.getValue(),"Landroid/widget/FrameLayout;",List.of(),null,List.of(),List.of(),List.of(method));
  DexPool.writeTo(file.toString(),new ImmutableDexFile(Opcodes.getDefault(),List.of(owner)));
  var mutable=new MutableClass(DexFileFactory.loadDexFile(file,Opcodes.getDefault()).getClasses().iterator().next());
  var original=mutable.getMethods().iterator().next();
  var preview=RoundedCardHookKt.installRoundedCardEntryBypass(mutable,t -> null);
  System.out.println("originalParameter="+original.getParameterTypes().get(0).getClass().getName());
  System.out.println("replacementParameter="+preview.getParameterTypes().get(0).getClass().getName());
  System.out.println("rawListEquals="+original.getParameterTypes().equals(preview.getParameterTypes()));
  if(original.getParameterTypes().equals(preview.getParameterTypes()))throw new AssertionError("RC regression not reproduced");
  if(args.length>1) {
   var cached=mutable.getVirtualMethods();
   var fn=RoundedCardHookKt.class.getDeclaredMethod("replaceRoundedCardEntryBypass",MutableClass.class,kotlin.jvm.functions.Function1.class);
   var replacement=(MutableMethod)fn.invoke(null,mutable,(kotlin.jvm.functions.Function1<String,ClassDef>)(t -> null));
   if(mutable.getMethods().iterator().next()!=replacement || cached.iterator().next()!=replacement)throw new AssertionError("wrong identity");
   DexPool.writeTo(file.toString(),new ImmutableDexFile(Opcodes.getDefault(),List.of(mutable)));
   var rewritten=DexFileFactory.loadDexFile(file,Opcodes.getDefault()).getClasses().iterator().next().getMethods().iterator().next();
   if(rewritten.getImplementation().getInstructions().iterator().next().getOpcode()!=Opcode.INVOKE_STATIC_RANGE)throw new AssertionError("guard lost");
   System.out.println("identityReplacementAndDexRoundtrip=PASS");
  }
 }
}
