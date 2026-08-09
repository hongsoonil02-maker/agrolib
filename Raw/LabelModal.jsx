import React from 'react';
import { useTranslation } from 'react-i18next';
import { LABEL_DATA } from '../data/labels';

const THEME_MAP = {
  monsmecta: {
    bg: 'bg-[#E8835A]/10',
    bodyBg: 'bg-[#170f06]',
    text: 'text-[#E8835A]',
    border: 'border-[#E8835A]',
    headerGradient: 'from-[#E8835A] via-[#F6C453] to-[#4A7C59]',
    accentBg: 'bg-[#E8835A]/10',
    accentText: 'text-[#F6C453]',
    buttonBorder: 'border-[#E8835A]/40 hover:border-[#E8835A]',
    buttonText: 'text-[#E8835A] hover:text-[#F6C453]'
  },
  hepamax: {
    bg: 'bg-[#D4AF37]/10',
    bodyBg: 'bg-[#1a1204]',
    text: 'text-[#D4AF37]',
    border: 'border-[#D4AF37]',
    headerGradient: 'from-[#D4AF37] via-[#F0D060] to-[#8B6D1E]',
    accentBg: 'bg-[#D4AF37]/10',
    accentText: 'text-[#F0D060]',
    buttonBorder: 'border-[#D4AF37]/40 hover:border-[#D4AF37]',
    buttonText: 'text-[#D4AF37] hover:text-[#F0D060]'
  },
  probiotics: {
    bg: 'bg-[#22C55E]/10',
    bodyBg: 'bg-[#05180c]',
    text: 'text-[#22C55E]',
    border: 'border-[#22C55E]',
    headerGradient: 'from-[#22C55E] via-[#86EFAC] to-[#15803D]',
    accentBg: 'bg-[#22C55E]/10',
    accentText: 'text-[#86EFAC]',
    buttonBorder: 'border-[#22C55E]/40 hover:border-[#22C55E]',
    buttonText: 'text-[#22C55E] hover:text-[#86EFAC]'
  },
  urinary: {
    bg: 'bg-[#6366F1]/10',
    bodyBg: 'bg-[#0a0a1f]',
    text: 'text-[#6366F1]',
    border: 'border-[#6366F1]',
    headerGradient: 'from-[#6366F1] via-[#A5B4FC] to-[#4338CA]',
    accentBg: 'bg-[#6366F1]/10',
    accentText: 'text-[#A5B4FC]',
    buttonBorder: 'border-[#6366F1]/40 hover:border-[#6366F1]',
    buttonText: 'text-[#6366F1] hover:text-[#A5B4FC]'
  },
  cancercare: {
    bg: 'bg-[#A855F7]/10',
    bodyBg: 'bg-[#140519]',
    text: 'text-[#A855F7]',
    border: 'border-[#A855F7]',
    headerGradient: 'from-[#A855F7] via-[#D8B4FE] to-[#7E22CE]',
    accentBg: 'bg-[#A855F7]/10',
    accentText: 'text-[#D8B4FE]',
    buttonBorder: 'border-[#A855F7]/40 hover:border-[#A855F7]',
    buttonText: 'text-[#A855F7] hover:text-[#D8B4FE]'
  },
  coldzero: {
    bg: 'bg-[#06B6D4]/10',
    bodyBg: 'bg-[#051519]',
    text: 'text-[#06B6D4]',
    border: 'border-[#06B6D4]',
    headerGradient: 'from-[#06B6D4] via-[#67E8F9] to-[#0E7490]',
    accentBg: 'bg-[#06B6D4]/10',
    accentText: 'text-[#67E8F9]',
    buttonBorder: 'border-[#06B6D4]/40 hover:border-[#06B6D4]',
    buttonText: 'text-[#06B6D4] hover:text-[#67E8F9]'
  },
  skincare: {
    bg: 'bg-[#EC4899]/10',
    bodyBg: 'bg-[#18060f]',
    text: 'text-[#EC4899]',
    border: 'border-[#EC4899]',
    headerGradient: 'from-[#EC4899] via-[#F9A8D4] to-[#BE185D]',
    accentBg: 'bg-[#EC4899]/10',
    accentText: 'text-[#F9A8D4]',
    buttonBorder: 'border-[#EC4899]/40 hover:border-[#EC4899]',
    buttonText: 'text-[#EC4899] hover:text-[#F9A8D4]'
  },
  heartcare: {
    bg: 'bg-[#EF4444]/10',
    bodyBg: 'bg-[#1a0505]',
    text: 'text-[#EF4444]',
    border: 'border-[#EF4444]',
    headerGradient: 'from-[#EF4444] via-[#FCA5A5] to-[#B91C1C]',
    accentBg: 'bg-[#EF4444]/10',
    accentText: 'text-[#FCA5A5]',
    buttonBorder: 'border-[#EF4444]/40 hover:border-[#EF4444]',
    buttonText: 'text-[#EF4444] hover:text-[#FCA5A5]'
  },
  jointcare: {
    bg: 'bg-[#84CC16]/10',
    bodyBg: 'bg-[#101703]',
    text: 'text-[#84CC16]',
    border: 'border-[#84CC16]',
    headerGradient: 'from-[#84CC16] via-[#BEF264] to-[#4D7C0F]',
    accentBg: 'bg-[#84CC16]/10',
    accentText: 'text-[#BEF264]',
    buttonBorder: 'border-[#84CC16]/40 hover:border-[#84CC16]',
    buttonText: 'text-[#84CC16] hover:text-[#BEF264]'
  },
  powerase: {
    bg: 'bg-[#F97316]/10',
    bodyBg: 'bg-[#190b02]',
    text: 'text-[#F97316]',
    border: 'border-[#F97316]',
    headerGradient: 'from-[#F97316] via-[#FDBA74] to-[#C2410C]',
    accentBg: 'bg-[#F97316]/10',
    accentText: 'text-[#FDBA74]',
    buttonBorder: 'border-[#F97316]/40 hover:border-[#F97316]',
    buttonText: 'text-[#F97316] hover:text-[#FDBA74]'
  },
  vitaplus: {
    bg: 'bg-[#EAB308]/10',
    bodyBg: 'bg-[#191504]',
    text: 'text-[#EAB308]',
    border: 'border-[#EAB308]',
    headerGradient: 'from-[#EAB308] via-[#FDE047] to-[#A16207]',
    accentBg: 'bg-[#EAB308]/10',
    accentText: 'text-[#FDE047]',
    buttonBorder: 'border-[#EAB308]/40 hover:border-[#EAB308]',
    buttonText: 'text-[#EAB308] hover:text-[#FDE047]'
  }
};

const LabelModal = ({ isLabelModalOpen, setIsLabelModalOpen, setIsPrintModalOpen, activeProduct }) => {
  const { t } = useTranslation();
  const labelData = LABEL_DATA[activeProduct] || LABEL_DATA['monsmecta'];
  const theme = THEME_MAP[activeProduct] || THEME_MAP['monsmecta'];

  if (!isLabelModalOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md transition-opacity" role="dialog" aria-modal="true" aria-labelledby="label-modal-title">
      <div className={`${theme.bodyBg} border ${theme.border} rounded-3xl shadow-2xl shadow-black/50 w-full max-w-4xl max-h-[90vh] overflow-y-auto relative animate-in fade-in zoom-in duration-300`}>
        <div className={`sticky top-0 bg-gradient-to-r ${theme.headerGradient} border-b ${theme.border} text-white p-6 flex justify-between items-center z-10`}>
          <div>
            <p className={`text-xs ${theme.text} font-bold tracking-widest uppercase mb-1`}>{t('label.header_eyebrow')}</p>
            <h3 id="label-modal-title" className="text-2xl font-black text-white">{t('label.header_title')}</h3>
          </div>
          <button onClick={() => setIsLabelModalOpen(false)} aria-label={t('common.close')} className="text-white/60 hover:text-white bg-white/5 hover:bg-white/10 rounded-full p-2 transition-colors">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-8">
          <div className="flex flex-col md:flex-row gap-8">
            <div className={`md:w-1/3 flex flex-col items-center border-r border-white/10 pr-0 md:pr-8`}>
              <div className={`${theme.accentBg} w-full p-6 flex justify-center items-center mb-6 border border-white/5 overflow-hidden`} style={{ borderRadius: '40px' }}>
                <img src={`${import.meta.env.BASE_URL}assets/${activeProduct === 'monsmecta' ? 'bottle' : activeProduct}_mockup.png`} alt={labelData.product_name} className="w-3/4 max-w-[200px] drop-shadow-[0_10px_20px_rgba(0,0,0,0.5)] hover:scale-105 transition-transform" style={{ borderRadius: '24px' }} />
              </div>
              <div className="w-full text-center">
                <h4 className={`text-xl font-black ${theme.text} mb-2`}>{labelData.product_name}</h4>
                <p className="text-sm font-bold text-gray-300 mb-4">{labelData.desc}</p>
                <div className={`space-y-2 text-left bg-white/5 border border-white/5 p-4 rounded-xl`}>
                  <p className={`text-xs font-bold ${theme.accentText} break-keep`}>{labelData.feed1}</p>
                  <p className={`text-xs font-bold ${theme.accentText} break-keep`}>{labelData.feed2}</p>
                  <p className={`text-xs font-bold ${theme.accentText} break-keep`}>{labelData.feed3}</p>
                </div>
              </div>
            </div>

            <div className="md:w-2/3 space-y-6">
              <div>
                <h5 className={`text-lg font-bold text-white border-b-2 ${theme.border} pb-2 mb-4 inline-block break-keep`}>{labelData.ingredients_title}</h5>
                <ul className="space-y-3 text-sm text-gray-300">
                  {labelData.ingredients.map((ing, i) => (
                    <li key={i} className="break-keep">
                      <strong className={theme.text}>{ing.title}</strong> <span className="text-gray-400">|</span> {ing.desc} 
                      {ing.note && <><br /><span className="text-xs text-gray-500 pl-4">{ing.note}</span></>}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm bg-white/5 p-5 rounded-2xl border border-white/10">
                <div className="col-span-full border-b border-white/10 pb-2 mb-2 flex justify-between items-end">
                  <span className="block text-xs font-bold text-gray-500 uppercase break-keep">{t('label.reg_no_title')}</span>
                  <strong className="text-white break-keep">{labelData.reg_no}</strong>
                </div>

                <div className="col-span-full">
                  <span className="block text-xs font-bold text-gray-500 uppercase mb-1 break-keep">{t('label.type_title')}</span>
                  <strong className="text-gray-200 break-keep">{labelData.type_val}</strong>
                </div>

                <div className="col-span-full">
                  <span className="block text-xs font-bold text-gray-500 uppercase mb-1 break-keep">{t('label.amount_title')}</span>
                  <strong className="text-gray-200 break-keep">{labelData.amount_val}</strong>
                </div>

                <div className="col-span-full">
                  <span className="block text-xs font-bold text-gray-500 uppercase mb-1 break-keep">{t('label.ingredients_list_title')}</span>
                  <strong className="text-gray-300 break-keep leading-relaxed">{labelData.ingredients_list_val}</strong>
                </div>

                <div className="col-span-full mt-2 bg-black/20 p-4 rounded-xl border border-white/5">
                  <span className={`block text-xs font-bold ${theme.text} uppercase mb-2 break-keep`}>{t('label.effect_title')}</span>
                  <ul className="text-gray-200 font-medium list-disc pl-4 mt-1 space-y-1.5">
                    {labelData.effects.map((eff, i) => (
                      <li key={i} className="break-keep">{eff}</li>
                    ))}
                  </ul>
                </div>

                <div className="flex justify-between items-center border-t border-white/10 pt-4 mt-2 col-span-full">
                  <div><span className="text-xs font-bold text-gray-500 uppercase break-keep">{t('label.weight_title')}</span> <strong className="text-gray-200 ml-1 break-keep">{labelData.weight_val}</strong></div>
                  <div><span className="text-xs font-bold text-gray-500 uppercase break-keep">{t('label.mfg_title')}</span> <span className="text-gray-400 ml-1 break-keep">{labelData.mfg_val}</span></div>
                </div>
                <div className="col-span-full pt-1">
                  <span className="text-xs font-bold text-gray-500 uppercase break-keep">{t('label.exp_title')}</span> <span className="text-gray-400 ml-1 break-keep">{labelData.exp_val}</span>
                </div>
              </div>

              <div className="bg-rose-950/40 text-rose-300 p-4 rounded-xl text-xs font-medium border border-rose-900/50">
                <span className="font-bold block mb-1 break-keep text-rose-400">{t('label.warning_title')}</span>
                <ul className="list-decimal pl-4 space-y-1 text-rose-300/80">
                  {labelData.warnings.map((warn, i) => (
                    <li key={i} className="break-keep">{warn}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="bg-black/40 p-6 border-t border-white/10 flex flex-col md:flex-row justify-between items-start md:items-center text-xs text-gray-400 rounded-b-3xl gap-4">
          <div className="flex flex-col sm:flex-row gap-6 w-full md:w-auto">
            <div className="flex items-center gap-3">
              <img src={`${import.meta.env.BASE_URL}assets/sj_logo.png`} alt="S&J" className="w-8 h-8 rounded-full border border-white/20 bg-black/50" />
              <div>
                <strong className="block text-gray-200">{t('label.seller_name')}</strong>
                {t('label.seller_addr')}<br />
                <span className={theme.text}>TEL</span> {t('label.seller_tel')}
              </div>
            </div>
            <div className="border-l-0 sm:border-l border-white/10 pl-0 sm:pl-6">
              <strong className="block text-gray-200">{t('label.maker_name')}</strong>
              {t('label.maker_addr')}<br />
              <span className={theme.text}>TEL</span> {t('label.maker_tel')}
            </div>
          </div>
          <button onClick={() => setIsPrintModalOpen(true)} className={`shrink-0 bg-black/40 border ${theme.buttonBorder} ${theme.buttonText} hover:bg-white/5 font-bold py-3 px-5 rounded-xl shadow-sm transition-colors flex items-center gap-2 w-full sm:w-auto justify-center`}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
            {t('label.print_btn')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LabelModal;
