using Xunit;
using static Backend.Models.HardwareCategory;

namespace Backend.Tests;

public class SimulationValidationTests
{
    [Fact]
    public void Unknown_probe_is_rejected() =>
        Assert.Contains("'nope'", Assert.Throws<ArgumentException>(() => Sim.Run("nope")).Message);

    [Fact]
    public void Unknown_component_is_rejected() =>
        Assert.Contains("'ghost'", Assert.Throws<ArgumentException>(() => Sim.Run("spirit", 10, "en", (Power, "ghost"))).Message);

    [Fact]
    public void Component_in_the_wrong_category_is_rejected()
    {
        var e = Assert.Throws<ArgumentException>(() => Sim.Run("spirit", 10, "en", (Power, "mli")));

        Assert.Contains("'mli'", e.Message);
        Assert.Contains("Power", e.Message);
    }

    [Fact]
    public void Probe_without_a_scenario_is_not_simulable()
    {
        var probe = TestHost.Store.Probes.First(p => p.Scenario is null);

        var e = Assert.Throws<ArgumentException>(() => Sim.Run(probe.Id));

        Assert.Contains("not available in the simulator", e.Message);
    }

    [Theory]
    [InlineData("en", "not found")]
    [InlineData("pt", "não encontrada")]
    [InlineData("es", "no encontrada")]
    [InlineData("fr", "introuvable")]
    public void Errors_are_translated(string lang, string expected) =>
        Assert.Contains(expected, Assert.Throws<ArgumentException>(() => Sim.Run("nope", null, lang)).Message);

    [Theory]
    [InlineData("en", "still working")]
    [InlineData("pt", "ainda funcionava")]
    [InlineData("es", "seguía funcionando")]
    [InlineData("fr", "fonctionnait encore")]
    public void Results_are_translated(string lang, string expected) =>
        Assert.Contains(expected, Sim.Run("viking-lander-1", 5, lang).EndReason);
}
