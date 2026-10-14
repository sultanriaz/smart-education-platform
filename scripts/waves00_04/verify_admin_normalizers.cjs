/** Transpile and execute the real Admin normalizers; install frontend deps first. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname,'../..');
const frontend=path.join(root,'apps','frontend');
const ts=require(require.resolve('typescript',{paths:[frontend]}));
const source=fs.readFileSync(path.join(frontend,'src/features/admin/normalizers.ts'),'utf8');
const output=ts.transpileModule(source,{fileName:'normalizers.ts',compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}, reportDiagnostics:true});
const errors=(output.diagnostics||[]).filter(x=>x.category===ts.DiagnosticCategory.Error);
if(errors.length)throw new Error('Typescript transpilation errors: '+errors.map(x=>x.messageText).join(';'));
const context={exports:{}};
vm.runInNewContext(output.outputText,context,{timeout:5000});
const st=context.exports.enrollment({id:'enrollment-1',student_profile_id:'student-profile-1',section_id:'section-1',status:'enrolled'});
const tch=context.exports.teachingAssignment({id:'assignment-1',teacher_profile_id:'teacher-profile-1',section_id:'section-1'});
if(st.studentUserId!=='student-profile-1')throw new Error('Enrollment did not preserve profile ID');
if(tch.teacherUserId!=='teacher-profile-1')throw new Error('Assignment did not preserve profile ID');
console.log('PASS actual frontend owner-response normalizers for Student and Teacher profile IDs');
