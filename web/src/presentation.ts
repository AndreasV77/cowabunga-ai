import type { Entry, Recipe } from './types';

export const sourceNames: Record<string, string> = { cookbook: 'Suno v6 Cookbook', 'lil-synn': 'LIL SYNN', 'band-manager': 'Band Manager', musai: 'MUSAI style recipes' };
export const recordTitle = (record: Entry | Recipe) => 'text' in record ? record.text : record.title;
export const recordField = (record: Entry | Recipe) => 'input_field' in record ? ({ style: 'Style wording', lyrics: 'Lyrics cue', settings: 'Control guidance' }[record.input_field || ''] || 'Method note') : 'Complete recipe';
