using Backend.Models;
using Xunit;

namespace Backend.Tests;

// Tries every possible combination of parts and checks rules that must always hold.
public class SimulationInvariantsTests
{
    [Theory]
    [InlineData("spirit", 120)]         // Mars rover, solar
    [InlineData("surveyor-3", 40)]      // Moon, crosses the lunar night
    [InlineData("ingenuity", 120)]      // helicopter (rotor wear and radiation rules)
    [InlineData("apollo-15-lrv", 5)]    // short Apollo mission
    public void Every_combination_of_parts_gives_a_valid_result(string probeId, int days)
    {
        var byCategory = TestHost.Store.Components
            .GroupBy(c => c.Category)
            .ToDictionary(g => g.Key, g => g.Select(c => c.Id).ToList());
        var planned = TestHost.Store.Probe(probeId)!.Scenario!.PlannedDurationDays;
        var combos = 0;

        foreach (var combo in Product(Enum.GetValues<HardwareCategory>(), byCategory))
        {
            var req = new SimulationRequest { ProbeId = probeId, TargetDays = days };
            foreach (var (cat, id) in combo) req.Components[cat] = id;

            var r = TestHost.Sim.Simulate(req, "en");
            combos++;
            var who = $"{probeId} + {string.Join(", ", combo.Select(c => c.Item2))}";

            Assert.True(r.Score is >= 0 and <= 100, $"{who}: score {r.Score}");
            Assert.True(r.DaysSurvived >= 0 && r.DaysSurvived <= days, $"{who}: survived {r.DaysSurvived} of {days}");
            Assert.True(r.MissionAccomplished == r.DaysSurvived >= planned, $"{who}: MissionAccomplished");
            Assert.False(string.IsNullOrWhiteSpace(r.EndReason), who);
            Assert.True(r.Events.Count <= 100, who);
            Assert.All(r.Events, e => Assert.True(e.Day >= 1, $"{who}: event on day {e.Day}"));
            Assert.Equal(r.Events.Select(e => e.Day).Order(), r.Events.Select(e => e.Day));
            Assert.True(r.Metrics.TotalMassKg >= 0, who);
            Assert.True(r.Metrics.RadiationReboots >= 0, who);
        }

        Assert.True(combos > 1000, $"only {combos} combinations were tried");
    }

    [Fact]
    public void Adding_target_days_never_shortens_the_survival()
    {
        foreach (var id in new[] { "spirit", "opportunity", "viking-lander-1", "apollo-12-alsep", "ingenuity" })
        {
            var shortRun = Sim.Run(id, 100).DaysSurvived;
            var longRun = Sim.Run(id, 400).DaysSurvived;

            Assert.True(longRun >= shortRun, $"{id}: {longRun} < {shortRun}");
        }
    }

    private static IEnumerable<List<(HardwareCategory, string)>> Product(
        HardwareCategory[] categories, Dictionary<HardwareCategory, List<string>> byCategory)
    {
        IEnumerable<List<(HardwareCategory, string)>> acc = [new()];
        foreach (var cat in categories)
        {
            var current = cat;
            acc = acc.SelectMany(prefix => byCategory[current].Select(id => new List<(HardwareCategory, string)>(prefix) { (current, id) }));
        }
        return acc;
    }
}
