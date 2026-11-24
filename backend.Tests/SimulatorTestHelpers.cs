using Backend.Models;

namespace Backend.Tests;

internal static class Sim
{
    public static SimulationResult Run(string probeId, int? days = null, string lang = "en",
        params (HardwareCategory Category, string ComponentId)[] overrides)
    {
        var req = new SimulationRequest { ProbeId = probeId, TargetDays = days };
        foreach (var (category, id) in overrides) req.Components[category] = id;
        return TestHost.Sim.Simulate(req, lang);
    }

    public static IEnumerable<object[]> SimulableProbes() =>
        TestHost.Store.Probes.Where(p => p.Scenario is not null).Select(p => new object[] { p.Id });
}
