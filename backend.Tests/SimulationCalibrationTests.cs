using Xunit;

namespace Backend.Tests;

// With the hardware the real probe had, the simulator should reproduce history:
// the mission succeeds and the probe lives about as long as the real one did.
public class SimulationCalibrationTests
{
    public static IEnumerable<object[]> Probes() => Sim.SimulableProbes();

    [Theory, MemberData(nameof(Probes))]
    public void Real_hardware_accomplishes_the_mission(string id)
    {
        var r = Sim.Run(id);

        Assert.True(r.MissionAccomplished, $"{id}: survived {r.DaysSurvived} of {r.PlannedDurationDays} planned days ({r.EndReason})");
        Assert.True(r.DaysSurvived >= r.PlannedDurationDays);
    }

    [Theory, MemberData(nameof(Probes))]
    public void Real_hardware_lives_close_to_the_real_duration(string id)
    {
        var r = Sim.Run(id);
        var actual = r.ActualDurationDays ?? r.PlannedDurationDays;

        Assert.InRange(r.DaysSurvived, (int)(actual * 0.8), actual);
    }

    [Theory, MemberData(nameof(Probes))]
    public void Real_hardware_scores_high(string id)
    {
        var score = Sim.Run(id).Score;

        Assert.True(score >= 75, $"{id} scored {score}");
    }

    [Fact]
    public void Real_hardware_defaults_equal_explicit_real_hardware()
    {
        var probe = TestHost.Store.Probe("spirit")!;
        var explicitHw = probe.RealHardware.Select(kv => (kv.Key, kv.Value)).ToArray();

        var a = Sim.Run("spirit");
        var b = Sim.Run("spirit", null, "en", explicitHw);

        Assert.Equal(a.DaysSurvived, b.DaysSurvived);
        Assert.Equal(a.Score, b.Score);
    }

    [Fact]
    public void Probe_ids_are_case_insensitive()
    {
        var a = Sim.Run("SPIRIT");

        Assert.Equal("spirit", a.ProbeId);
    }

    [Fact]
    public void Simulation_is_deterministic()
    {
        var a = Sim.Run("opportunity");
        var b = Sim.Run("opportunity");

        Assert.Equal(a.DaysSurvived, b.DaysSurvived);
        Assert.Equal(a.Score, b.Score);
        Assert.Equal(a.Events, b.Events);
    }

    [Fact]
    public void Dust_storm_of_2018_ends_opportunity()
    {
        var r = Sim.Run("opportunity");

        Assert.Contains("Out of power", r.EndReason);
        Assert.InRange(r.DaysSurvived, 5200, 5251);   // the storm starts on day 5235
    }
}
