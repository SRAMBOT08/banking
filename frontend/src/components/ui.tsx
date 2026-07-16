'use client';
import { Box, Chip, LinearProgress, Paper, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';

export const Panel = ({ children, title, action }: {children: ReactNode; title?: string; action?: ReactNode}) => <Paper elevation={0} sx={{p:2,border:'1px solid #334155',borderRadius:'6px',background:'#17243a',height:'100%'}}>{title && <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{mb:1.5}}><Typography sx={{fontSize:13,fontWeight:700,letterSpacing:.3}}>{title}</Typography>{action}</Stack>}{children}</Paper>;
export const StatusChip = ({label, color='default'}: {label:string;color?:'default'|'success'|'warning'|'error'|'info'}) => <Chip label={label} size="small" color={color} sx={{height:22,fontSize:11,fontWeight:700,borderRadius:'4px'}} />;
export const Kpi = ({label,value,detail,tone='blue'}: {label:string;value:string;detail:string;tone?:'blue'|'red'|'green'|'amber'}) => <Panel><Typography color="text.secondary" sx={{fontSize:11,fontWeight:700,textTransform:'uppercase',letterSpacing:1}}>{label}</Typography><Typography sx={{fontSize:27,fontWeight:800,mt:1}}>{value}</Typography><Typography sx={{fontSize:11,color:tone==='red'?'#f87171':tone==='green'?'#4ade80':tone==='amber'?'#fbbf24':'#38bdf8',mt:.5}}>{detail}</Typography></Panel>;
export const Progress = ({value,color='#2563eb'}:{value:number;color?:string}) => <LinearProgress variant="determinate" value={value} sx={{height:5,borderRadius:3,bgcolor:'#27364f','& .MuiLinearProgress-bar':{bgcolor:color,borderRadius:3}}}/>;
