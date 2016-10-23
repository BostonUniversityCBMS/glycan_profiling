from .chromatogram_artist import (
    SmoothingChromatogramArtist, AbundantLabeler,
    NGlycanLabelProducer, n_glycan_colorizer)

from .entity_bar_chart import AggregatedAbundanceArtist
from .utils import figax


class GlycanChromatographySummaryGraphBuilder(object):
    def __init__(self, solutions):
        self.solutions = solutions

    def chromatograms(self, min_score=0.4, min_signal=0.2, colorizer=None, total_ion_chromatogram=None,
                      base_peak_chromatogram=None):
        monosaccharides = set()

        for sol in self.solutions:
            if sol.glycan_composition:
                monosaccharides.update(map(str, sol.glycan_composition))

        label_abundant = AbundantLabeler(
            NGlycanLabelProducer(monosaccharides),
            max(sol.total_signal for sol in self.solutions if sol.score > min_score) * min_signal)

        if colorizer is None:
            colorizer = n_glycan_colorizer

        results = [sol for sol in self.solutions if sol.score > min_score and not sol.used_as_adduct]
        chrom = SmoothingChromatogramArtist(results, ax=figax(), colorizer=colorizer).draw(label_function=label_abundant)

        if total_ion_chromatogram is not None:
            rt, intens = total_ion_chromatogram.as_arrays()
            chrom.draw_generic_chromatogram(
                "TIC", rt, intens, 'blue')
            chrom.ax.set_ylim(0, max(intens) * 1.1)

        if base_peak_chromatogram is not None:
            rt, intens = base_peak_chromatogram.as_arrays()
            chrom.draw_generic_chromatogram(
                "BPC", rt, intens, 'green')
        return chrom

    def aggregated_abundance(self, min_score=0.4):
        agg = AggregatedAbundanceArtist([
            sol for sol in self.solutions if sol.score > min_score and not sol.used_as_adduct],
            ax=figax())
        agg.draw()
        return agg

    def draw(self, min_score=0.4, min_signal=0.2, colorizer=None, total_ion_chromatogram=None,
             base_peak_chromatogram=None):
        chrom = self.chromatograms(min_score, min_signal, colorizer,
                                   total_ion_chromatogram, base_peak_chromatogram)
        agg = self.aggregated_abundance(min_score)
        return chrom, agg