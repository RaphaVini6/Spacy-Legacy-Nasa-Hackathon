using Xunit;
using static Backend.Models.HardwareCategory;

namespace Backend.Tests;

// One test per rule of the model, using the real probes and parts.
public class SimulationRulesTests
{
    [Fact]
    public void Uhf_relay_radio_cannot_work_on_the_moon()
    {
        var r = Sim.Run("surveyor-3", null, "en", (Communication, "uhf-relay"));

        Assert.Equal(0, r.DaysSurvived);
        Assert.Equal(0, r.Score);
        Assert.False(r.MissionAccomplished);
        Assert.Contains("No communication", r.EndReason);
    }

    [Fact]
    public void Uhf_relay_radio_works_on_mars_where_there_are_orbiters()
    {
        var r = Sim.Run("spirit", 50);   // spirit's real radio is already UHF

        Assert.Equal(50, r.DaysSurvived);
    }

    [Fact]
    public void Helicopter_rotor_cannot_fly_on_the_moon()
    {
        var r = Sim.Run("surveyor-3", null, "en", (Mobility, "carbon-fiber-rotor"));

        Assert.Equal(0, r.DaysSurvived);
        Assert.Contains("no air", r.EndReason);
    }

    [Fact]
    public void Probe_without_insulation_freezes_on_the_first_martian_night()
    {
        var r = Sim.Run("spirit", null, "en", (Thermal, "no-thermal-protection"));

        Assert.Equal(0, r.DaysSurvived);
        Assert.Contains("Froze", r.EndReason);
        Assert.True(r.Metrics.MinSupportedTempC > -90);
    }

    [Fact]
    public void Rtg_and_insulation_widen_the_cold_limit()
    {
        var bare = Sim.Run("perseverance", 10, "en", (Thermal, "no-thermal-protection"), (Power, "solar-panels"));
        var insulated = Sim.Run("perseverance", 10);

        Assert.True(insulated.Metrics.MinSupportedTempC < bare.Metrics.MinSupportedTempC);
    }

    [Fact]
    public void Solar_probe_dies_on_the_first_lunar_night()
    {
        // surveyor-3 is solar powered: ~14.75 days of light, then the lunar night (-173 C)
        var r = Sim.Run("surveyor-3", 30);

        Assert.InRange(r.DaysSurvived, 14, 16);
        Assert.Contains("Froze", r.EndReason);
    }

    [Fact]
    public void Rtg_probe_survives_the_lunar_night()
    {
        var r = Sim.Run("apollo-12-alsep", 100);   // 3+ lunar days

        Assert.Equal(100, r.DaysSurvived);
        Assert.Contains("still working", r.EndReason);
    }

    [Fact]
    public void Overheating_is_a_warning_not_a_death()
    {
        // the real scenario has a 60 C maximum; without insulation the parts only tolerate 50 C
        var r = Sim.Run("apollo-11-eagle", null, "en", (Thermal, "no-thermal-protection"));

        Assert.Contains(r.Events, e => e.Type == "Heat" && e.Day == 1);
        Assert.True(r.MissionAccomplished);
    }

    [Fact]
    public void Insulation_prevents_the_overheating_warning()
    {
        var r = Sim.Run("apollo-11-eagle");   // real hardware: multi-layer insulation

        Assert.DoesNotContain(r.Events, e => e.Type == "Heat");
    }

    [Fact]
    public void Missing_battery_means_death_in_the_dark()
    {
        var r = Sim.Run("spirit", 100, "en", (Storage, "no-battery"));

        Assert.Equal(0, r.DaysSurvived);
        Assert.Contains("No usable battery", r.EndReason);
    }

    [Fact]
    public void Missing_power_source_drains_the_battery_then_ends()
    {
        var r = Sim.Run("spirit", 100, "en", (Power, "no-power-source"));

        Assert.InRange(r.DaysSurvived, 1, 10);
        Assert.Contains("battery ran out", r.EndReason);
        Assert.Contains(r.Events, e => e.Type == "Power");
    }

    [Fact]
    public void Low_power_makes_the_probe_hibernate_and_wake_up()
    {
        var r = Sim.Run("spirit");   // Mars winter: not enough sun for some days

        Assert.Contains(r.Events, e => e.Type == "Power" && e.Message.Contains("hibernation"));
        Assert.Contains(r.Events, e => e.Type == "Power" && e.Message.Contains("wakes up"));
    }

    [Fact]
    public void Hibernation_summary_is_reported_for_a_short_run()
    {
        var r = Sim.Run("spirit", 150);   // first hibernation starts on day 142, few events

        Assert.Contains(r.Events, e => e.Type == "Summary");
    }

    // Long runs have hundreds of hibernate/wake-up events; the late key events must survive the 100 cap.
    [Fact]
    public void Important_late_events_are_not_lost_when_there_are_many_events()
    {
        var r = Sim.Run("opportunity");

        Assert.Contains(r.Events, e => e.Type == "End");
        Assert.Contains(r.Events, e => e.Type == "Storm");
        Assert.Contains(r.Events, e => e.Type == "Summary");
    }

    [Fact]
    public void Wind_cleaning_event_only_happens_when_the_scenario_allows_it()
    {
        var spirit = Sim.Run("spirit");   // WindCleansPanels = true

        Assert.Contains(spirit.Events, e => e.Type == "Dust");
        Assert.DoesNotContain(Sim.Run("mars-pathfinder").Events, e => e.Type == "Dust");
    }

    [Fact]
    public void Dust_on_the_panels_eventually_ends_the_pathfinder()
    {
        var r = Sim.Run("mars-pathfinder");

        Assert.True(r.MissionAccomplished);
        Assert.Contains("Out of power", r.EndReason);
    }

    [Fact]
    public void Computer_with_low_radiation_tolerance_reboots_and_a_hardened_one_does_not()
    {
        var real = Sim.Run("ingenuity");   // snapdragon: tolerance 3 vs Mars radiation 5

        Assert.True(real.Metrics.RadiationReboots > 10);
        Assert.Contains(real.Events, e => e.Type == "Radiation");

        var hardened = Sim.Run("ingenuity", null, "en", (Computer, "rad750"));
        Assert.Equal(0, hardened.Metrics.RadiationReboots);
    }

    [Fact]
    public void Commercial_processor_on_the_moon_is_destroyed_by_radiation_after_30_days()
    {
        var r = Sim.Run("apollo-12-alsep", 400, "en", (Computer, "snapdragon"));

        Assert.Equal(29, r.DaysSurvived);
        Assert.Contains("Radiation permanently damaged", r.EndReason);
        Assert.False(r.MissionAccomplished);
    }

    [Fact]
    public void Worn_out_wheels_only_stop_the_probe_they_do_not_kill_it()
    {
        // steel mesh wheels last 30 days
        var r = Sim.Run("spirit", 100, "en", (Mobility, "steel-mesh-wheels"));

        Assert.Equal(100, r.DaysSurvived);
        Assert.Contains(r.Events, e => e.Type == "Mobility" && e.Day == 30);
    }

    [Fact]
    public void Rotor_wear_destroys_the_helicopter()
    {
        var r = Sim.Run("ingenuity", 2000);   // the carbon rotor lasts 1020 days

        Assert.True(r.DaysSurvived <= 1020);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-5)]
    public void Target_days_below_one_is_raised_to_one(int requested) =>
        Assert.Equal(1, Sim.Run("viking-lander-1", requested).DaysSurvived);

    [Fact]
    public void Target_days_is_capped_at_7000()
    {
        var r = Sim.Run("viking-lander-1", 99999);

        Assert.Equal(7000, r.DaysSurvived);
        Assert.Contains("7000", r.EndReason);
    }

    [Fact]
    public void Shorter_target_days_stop_the_simulation_early()
    {
        var r = Sim.Run("viking-lander-1", 10);

        Assert.Equal(10, r.DaysSurvived);
        Assert.False(r.MissionAccomplished);   // planned is 90 days
    }

    [Fact]
    public void Metrics_add_up_the_mass_and_consumption_of_the_chosen_parts()
    {
        var probe = TestHost.Store.Probe("spirit")!;
        var parts = probe.RealHardware.Values.Select(id => TestHost.Store.Component(id)!).ToList();

        var r = Sim.Run("spirit", 10);

        Assert.Equal(Math.Round(parts.Sum(p => p.MassKg), 1), r.Metrics.TotalMassKg);
        Assert.Equal(parts.Sum(p => p.ConsumptionW), r.Metrics.BaseConsumptionW);
        Assert.Equal(TestHost.Store.Component("lithium-ion")!.CapacityWh, r.Metrics.BatteryCapacityWh);
    }

    [Fact]
    public void Solar_output_on_mars_is_scaled_by_irradiance()
    {
        var r = Sim.Run("spirit", 1);
        var panels = TestHost.Store.Component("solar-panels")!;

        Assert.Equal(Math.Round(panels.OutputW * 590 / 1361, 1), r.Metrics.InitialOutputW);
    }

    [Fact]
    public void Rtg_output_does_not_depend_on_sunlight()
    {
        var r = Sim.Run("apollo-12-alsep", 1);

        Assert.Equal(TestHost.Store.Component("rtg-snap27")!.OutputW, r.Metrics.InitialOutputW);
    }

    [Fact]
    public void Score_rewards_surviving_the_real_duration()
    {
        var full = Sim.Run("viking-lander-1");
        var half = Sim.Run("viking-lander-1", 1150);

        Assert.True(full.Score > half.Score);
        Assert.Equal(100, full.Score);
    }

    [Fact]
    public void Events_are_sorted_by_day_and_capped_at_100()
    {
        var r = Sim.Run("opportunity");

        Assert.True(r.Events.Count <= 100);
        Assert.Equal(r.Events.Select(e => e.Day).Order(), r.Events.Select(e => e.Day));
    }

    [Fact]
    public void Real_hardware_of_the_probe_is_returned_for_comparison()
    {
        var r = Sim.Run("spirit", 5, "en", (Power, "mmrtg"));

        Assert.Equal("solar-panels", r.RealHardware[Power]);
    }
}
