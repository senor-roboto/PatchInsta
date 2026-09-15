import com.android.tools.smali.dexlib2.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.dexlib2.iface.instruction.*;
import com.android.tools.smali.dexlib2.iface.reference.*;
import java.io.File;
import java.util.*;
public class VerifyFoldDex {
 static final String EXT="Lapp/morphe/extension/instagram/patches/reels/FoldReels;";
 static void require(boolean b,String s){if(!b)throw new AssertionError(s);}
 static Map<String,ClassDef> load(String path)throws Exception {
  var container=DexFileFactory.loadDexContainer(new File(path),Opcodes.getDefault());var result=new HashMap<String,ClassDef>();
  int duplicates=0;
  for(String entry:container.getDexEntryNames())for(ClassDef c:container.getEntry(entry).getDexFile().getClasses())if(result.putIfAbsent(c.getType(),c)!=null){
   duplicates++;require(!c.getType().equals(EXT)&&!c.getType().endsWith("/RoundedCornerFrameLayout;"),"Duplicate audited class "+c.getType());
  }
  System.out.println("Input "+path+": "+result.size()+" unique classes; "+duplicates+" duplicate definitions.");
  require(duplicates==0,"Duplicate class definitions in final APK");
  return result;
 }
 static Method method(ClassDef c,String name){for(Method m:c.getMethods())if(m.getName().equals(name))return m;throw new AssertionError(name);}
 static List<Instruction> code(Method m){var result=new ArrayList<Instruction>();m.getImplementation().getInstructions().forEach(result::add);return result;}
 static String key(Instruction i){
  String s=i.getOpcode().toString();
  if(i instanceof OneRegisterInstruction x)s+=" a="+x.getRegisterA();
  if(i instanceof TwoRegisterInstruction x)s+=" b="+x.getRegisterB();
  if(i instanceof ThreeRegisterInstruction x)s+=" c="+x.getRegisterC();
  if(i instanceof FiveRegisterInstruction x)s+=" regs="+x.getRegisterCount()+","+x.getRegisterC()+","+x.getRegisterD()+","+x.getRegisterE()+","+x.getRegisterF()+","+x.getRegisterG();
  if(i instanceof RegisterRangeInstruction x)s+=" range="+x.getStartRegister()+","+x.getRegisterCount();
  if(i instanceof WideLiteralInstruction x)s+=" literal="+x.getWideLiteral();
  if(i instanceof OffsetInstruction x)s+=" offset="+x.getCodeOffset();
  if(i instanceof ReferenceInstruction x)s+=" ref="+x.getReference();
  return s;
 }
 public static void main(String[] args)throws Exception {
  var old=load(args[0]);var patched=load(args[1]);String rounded="Lcom/instagram/ui/widget/roundedcornerlayout/RoundedCornerFrameLayout;";
  require(patched.keySet().containsAll(old.keySet()),"Missing original classes");
  Method a=method(old.get(rounded),"dispatchDraw"),b=method(patched.get(rounded),"dispatchDraw");var x=code(a);var y=code(b);
  require(y.size()==x.size()+5,"5 instruction prefix");require(a.getImplementation().getRegisterCount()==b.getImplementation().getRegisterCount(),"registers changed");
  for(int i=0;i<x.size();i++)require(key(x.get(i)).equals(key(y.get(i+5))),"native instruction mismatch "+i);
  require(y.get(0).getOpcode()==Opcode.INVOKE_STATIC_RANGE && ((ReferenceInstruction)y.get(0)).getReference().toString().equals(EXT+"->skipRoundedCardDecoration(Landroid/view/View;)Z"),"guard");
  require(y.get(1).getOpcode()==Opcode.MOVE_RESULT && y.get(2).getOpcode()==Opcode.IF_EQZ && ((OffsetInstruction)y.get(2)).getCodeOffset()==6,"guard fallback");
  require(y.get(3).getOpcode()==Opcode.INVOKE_SUPER_RANGE && y.get(4).getOpcode()==Opcode.RETURN_VOID,"native bypass");
  int self=a.getImplementation().getRegisterCount()-2;
  RegisterRangeInstruction guard=(RegisterRangeInstruction)y.get(0),parent=(RegisterRangeInstruction)y.get(3);
  require(guard.getStartRegister()==self && guard.getRegisterCount()==1 && parent.getStartRegister()==self && parent.getRegisterCount()==2,"receiver/Canvas registers");
  require(((OneRegisterInstruction)y.get(1)).getRegisterA()==0 && ((OneRegisterInstruction)y.get(2)).getRegisterA()==0,"guard scratch register");
  String parentRef=((ReferenceInstruction)y.get(3)).getReference().toString();
  require(x.stream().anyMatch(i -> (i.getOpcode()==Opcode.INVOKE_SUPER || i.getOpcode()==Opcode.INVOKE_SUPER_RANGE) && ((ReferenceInstruction)i).getReference().toString().equals(parentRef)),"native parent call changed");
  var triesA=a.getImplementation().getTryBlocks();var triesB=b.getImplementation().getTryBlocks();require(triesA.size()==triesB.size(),"try count");
  for(int i=0;i<triesA.size();i++){var t=triesA.get(i);var u=triesB.get(i);require(u.getStartCodeAddress()==t.getStartCodeAddress()+10 && u.getCodeUnitCount()==t.getCodeUnitCount(),"try shift");
   require(t.getExceptionHandlers().size()==u.getExceptionHandlers().size(),"handler count");for(int j=0;j<t.getExceptionHandlers().size();j++){var h=t.getExceptionHandlers().get(j);var k=u.getExceptionHandlers().get(j);require(Objects.equals(h.getExceptionType(),k.getExceptionType())&&k.getHandlerCodeAddress()==h.getHandlerCodeAddress()+10,"handler shift");}}
  var expected=new LinkedHashMap<String,Integer>();expected.put("attachViewer",2);expected.put("beforeViewerDraw",1);expected.put("routeTouch",1);expected.put("skipRoundedCardDecoration",1);var counts=new HashMap<String,Integer>();
  require(patched.containsKey(EXT),"extension absent");
  for(ClassDef c:patched.values())if(!c.getType().startsWith("Lapp/morphe/extension/"))for(Method m:c.getMethods())if(m.getImplementation()!=null)for(Instruction ins:m.getImplementation().getInstructions()){
   if(ins instanceof ReferenceInstruction ri && ri.getReference() instanceof MethodReference ref && ref.getDefiningClass().equals(EXT) && expected.containsKey(ref.getName())){
    require(ins.getOpcode()==Opcode.INVOKE_STATIC_RANGE || ins.getOpcode()==Opcode.INVOKE_STATIC,"hook call kind");counts.merge(ref.getName(),1,Integer::sum);
    boolean found=false;for(Method target:patched.get(EXT).getMethods())if(target.toString().equals(ref.toString())){require((target.getAccessFlags()&9)==9 && target.getImplementation()!=null,"hook prototype");found=true;}require(found,"unresolved hook "+ref);
   }
  }
  require(counts.equals(expected),"hook counts "+counts);
  System.out.println("PASS Rounded: "+x.size()+" native instructions unchanged; 5-instruction/10-code-unit guard; registers, branches, try/handlers preserved.");
  System.out.println("PASS generated hooks and public static executable prototypes: "+counts);
  System.out.println("STATIC ONLY. No ART verification, installation, decoder or Samsung pixel execution.");
 }
}
