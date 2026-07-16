export type Severity = 'Critical' | 'High' | 'Medium' | 'Low';
export type Module = 'Overview' | 'Investigations' | 'Investigation Workspace' | 'Attack Simulator' | 'Threat Intelligence' | 'Knowledge Platform' | 'MITRE ATT&CK' | 'System Health' | 'Settings';

export const investigations = [
  { id:'INV-2026-0418', title:'Credential stuffing campaign', severity:'Critical' as Severity, status:'AI reasoning', confidence:94, threat:'APT-41', customer:'Northstar Bank', updated:'2 min ago', mitre:'T1110.004' },
  { id:'INV-2026-0417', title:'Impossible travel + session theft', severity:'High' as Severity, status:'Case created', confidence:87, threat:'UNC3944', customer:'Apex Retail', updated:'11 min ago', mitre:'T1078' },
  { id:'INV-2026-0416', title:'Large beneficiary transfer', severity:'High' as Severity, status:'Awaiting approval', confidence:81, threat:'FIN12', customer:'Meridian Finance', updated:'24 min ago', mitre:'T1653' },
  { id:'INV-2026-0415', title:'Insider data staging', severity:'Medium' as Severity, status:'Completed', confidence:76, threat:'Unknown', customer:'Helix Health', updated:'1 hr ago', mitre:'T1074' },
  { id:'INV-2026-0414', title:'Password spray burst', severity:'Medium' as Severity, status:'Completed', confidence:72, threat:'Volt Typhoon', customer:'Orion Energy', updated:'2 hrs ago', mitre:'T1110.003' },
];
export const timeline = [
  ['09:42:18','EVENT','3,842 authentication failures normalized','Ingestion Service'],['09:42:24','EVIDENCE','14 entities resolved · 9 relationships built','Evidence Intelligence'],['09:42:31','THREAT','Credential stuffing pattern matched at 94%','Threat Intelligence'],['09:42:39','INVESTIGATION','Investigation graph reached confidence threshold','Investigation Service'],['09:42:45','CASE','Immutable CaseFile v1 persisted','Case Builder'],['09:42:52','AI','8 reports generated with provenance','AI Report Service'],['09:43:01','EXECUTION','Policy evaluated · 2 actions awaiting approval','Execution Service'],
] as const;
export const health = [['Kafka','Healthy','12ms'],['Evidence Graph','Healthy','18ms'],['PostgreSQL','Healthy','7ms'],['Redis','Healthy','3ms'],['NVIDIA NIM','Degraded','842ms'],['ServiceNow','Healthy','126ms']];
