import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Building2,
  Grid2X2,
  List,
  MapPin,
  Plus,
  Search,
  Sprout,
} from "lucide-react";
import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useOfflineSync } from "../app/OfflineSync";
import { PageHeader } from "../components/PageHeader";
import { useToast } from "../components/Toast";
import {
  Alert,
  Badge,
  Button,
  Card,
  EmptyState,
  Modal,
  PageSkeleton,
} from "../components/ui";
import { ApiError, api } from "../services/api";
import { enqueueRecord } from "../services/offlineDb";
import type { FarmCreate, FieldCreate } from "../types/api";

const farmSchema = z.object({
  name: z.string().min(2, "Enter a farm name.").max(120),
  contact_name: z.string().max(120),
  province: z.string().min(2, "Select or enter a province.").max(80),
  district: z.string().min(2, "Enter a district.").max(80),
  ward: z.string().max(80),
  latitude: z.union([z.literal(""), z.coerce.number().min(-90).max(90)]),
  longitude: z.union([z.literal(""), z.coerce.number().min(-180).max(180)]),
  notes: z.string().max(2000),
});

const fieldSchema = z.object({
  farm_id: z.string().min(1, "Choose a farm."),
  name: z.string().min(1, "Enter a field name.").max(120),
  size_hectares: z.coerce
    .number()
    .positive("Field size must be above zero.")
    .max(10000),
  maize_variety: z.string().max(100),
  planting_date: z.string(),
  season: z.string().min(1).max(30),
  target_yield_t_ha: z.union([z.literal(""), z.coerce.number().min(0).max(30)]),
  notes: z.string().max(2000),
});

type FarmForm = z.infer<typeof farmSchema>;
type FieldForm = z.infer<typeof fieldSchema>;

export default function FarmsPage() {
  const [search, setSearch] = useState("");
  const [view, setView] = useState<"cards" | "table">("cards");
  const [farmOpen, setFarmOpen] = useState(false);
  const [fieldOpen, setFieldOpen] = useState(false);
  const farms = useQuery({ queryKey: ["farms"], queryFn: api.farms });
  const fields = useQuery({
    queryKey: ["fields"],
    queryFn: () => api.fields(),
  });
  const queryClient = useQueryClient();
  const { online, refreshCounts } = useOfflineSync();
  const { notify } = useToast();

  const farmForm = useForm<FarmForm>({
    resolver: zodResolver(farmSchema),
    defaultValues: {
      name: "",
      contact_name: "",
      province: "",
      district: "",
      ward: "",
      latitude: "",
      longitude: "",
      notes: "",
    },
  });
  const fieldForm = useForm<FieldForm>({
    resolver: zodResolver(fieldSchema),
    defaultValues: {
      farm_id: "",
      name: "",
      size_hectares: 1,
      maize_variety: "",
      planting_date: "",
      season: "2025/26",
      target_yield_t_ha: "",
      notes: "",
    },
  });

  const createFarm = useMutation({
    mutationFn: api.createFarm,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["farms"] });
      farmForm.reset();
      setFarmOpen(false);
      notify("Farm saved");
    },
  });
  const createField = useMutation({
    mutationFn: api.createField,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["fields"] }),
        queryClient.invalidateQueries({ queryKey: ["farms"] }),
      ]);
      fieldForm.reset();
      setFieldOpen(false);
      notify("Field saved");
    },
  });

  const saveFarm = async (values: FarmForm) => {
    const payload: FarmCreate = {
      id: crypto.randomUUID(),
      name: values.name,
      contact_name: values.contact_name,
      province: values.province,
      district: values.district,
      ward: values.ward,
      latitude: values.latitude === "" ? null : values.latitude,
      longitude: values.longitude === "" ? null : values.longitude,
      notes: values.notes,
    };
    if (online) {
      try {
        await createFarm.mutateAsync(payload);
        return;
      } catch (error) {
        if (error instanceof ApiError && error.status < 500) return;
      }
    }
    await enqueueRecord("farm", { ...payload });
    await refreshCounts();
    setFarmOpen(false);
    farmForm.reset();
    notify("Farm saved offline and queued for synchronization");
  };

  const saveField = async (values: FieldForm) => {
    const payload: FieldCreate = {
      id: crypto.randomUUID(),
      farm_id: values.farm_id,
      name: values.name,
      size_hectares: values.size_hectares,
      maize_variety: values.maize_variety,
      planting_date: values.planting_date || null,
      season: values.season,
      target_yield_t_ha:
        values.target_yield_t_ha === "" ? null : values.target_yield_t_ha,
      notes: values.notes,
    };
    if (online) {
      try {
        await createField.mutateAsync(payload);
        return;
      } catch (error) {
        if (error instanceof ApiError && error.status < 500) return;
      }
    }
    await enqueueRecord("field", { ...payload });
    await refreshCounts();
    setFieldOpen(false);
    fieldForm.reset();
    notify("Field saved offline and queued for synchronization");
  };

  const filtered = useMemo(() => {
    const needle = search.trim().toLowerCase();
    return (farms.data ?? []).filter(
      (farm) =>
        !needle ||
        [farm.name, farm.province, farm.district, farm.ward].some((value) =>
          value.toLowerCase().includes(needle),
        ),
    );
  }, [farms.data, search]);

  if (farms.isLoading || fields.isLoading) return <PageSkeleton />;

  return (
    <div className="page-enter">
      <PageHeader
        eyebrow="Farm registry"
        title="Farms and fields"
        body="Keep reusable farm context separate from immutable assessment snapshots. Demonstration records are clearly labelled."
        actions={
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => setFarmOpen(true)}>
              <Plus className="size-4" />
              Add farm
            </Button>
            <Button
              onClick={() => setFieldOpen(true)}
              disabled={!farms.data?.length}
            >
              <Sprout className="size-4" />
              Add field
            </Button>
          </div>
        }
      />
      {!online && (
        <Alert tone="warning" title="Working offline">
          New farms and fields will be stored on this device and synchronized
          when the local service returns.
        </Alert>
      )}
      <Card className="mt-5 flex flex-col gap-3 p-4 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <span className="sr-only">Search farms</span>
          <Search className="pointer-events-none absolute left-3 top-3 size-5 text-muted" />
          <input
            className="input pl-10"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search farm, province, district, or ward"
          />
        </label>
        <div
          className="flex rounded-xl border border-line p-1"
          aria-label="View style"
        >
          <button
            className={`icon-button ${view === "cards" ? "bg-pale text-deep" : ""}`}
            onClick={() => setView("cards")}
            aria-label="Card view"
          >
            <Grid2X2 className="size-5" />
          </button>
          <button
            className={`icon-button ${view === "table" ? "bg-pale text-deep" : ""}`}
            onClick={() => setView("table")}
            aria-label="Table view"
          >
            <List className="size-5" />
          </button>
        </div>
      </Card>
      {!filtered.length ? (
        <div className="mt-5">
          <EmptyState
            icon={<Building2 className="size-6" />}
            title="No farms yet"
            body="Create a farm, then add one or more maize fields for faster assessments."
            action={
              <Button onClick={() => setFarmOpen(true)}>Add first farm</Button>
            }
          />
        </div>
      ) : view === "cards" ? (
        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((farm) => (
            <Card key={farm.id} className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="grid size-11 place-items-center rounded-xl bg-teal/10 text-teal">
                  <Building2 className="size-6" />
                </div>
                <div className="flex gap-1">
                  {farm.is_demo && <Badge tone="gold">Demo</Badge>}
                  <Badge
                    tone={
                      farm.sync_status === "synchronized" ? "green" : "gold"
                    }
                  >
                    {farm.sync_status}
                  </Badge>
                </div>
              </div>
              <h2 className="mt-4 text-xl font-extrabold text-ink">
                {farm.name}
              </h2>
              <p className="mt-2 flex items-center gap-2 text-sm text-muted">
                <MapPin className="size-4" />
                {farm.district}, {farm.province}
                {farm.ward ? ` · Ward ${farm.ward}` : ""}
              </p>
              <div className="mt-4 flex items-center justify-between border-t border-line pt-4">
                <span className="text-sm text-muted">
                  {farm.field_count}{" "}
                  {farm.field_count === 1 ? "field" : "fields"}
                </span>
                <span className="text-sm font-bold text-ink">
                  {farm.contact_name || "No contact recorded"}
                </span>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="mt-5 overflow-x-auto rounded-2xl border border-line bg-white">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="bg-pale text-xs uppercase text-muted">
              <tr>
                <th className="p-3">Farm</th>
                <th className="p-3">Location</th>
                <th className="p-3">Contact</th>
                <th className="p-3">Fields</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((farm) => (
                <tr key={farm.id} className="border-t border-line">
                  <td className="p-3 font-bold text-ink">{farm.name}</td>
                  <td className="p-3">
                    {farm.district}, {farm.province}
                  </td>
                  <td className="p-3">{farm.contact_name || "—"}</td>
                  <td className="p-3">{farm.field_count}</td>
                  <td className="p-3">
                    <Badge
                      tone={
                        farm.sync_status === "synchronized" ? "green" : "gold"
                      }
                    >
                      {farm.sync_status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={farmOpen}
        title="Add a farm"
        onClose={() => setFarmOpen(false)}
      >
        <form className="grid gap-4" onSubmit={farmForm.handleSubmit(saveFarm)}>
          <div className="grid gap-4 sm:grid-cols-2">
            <label>
              <span className="label">Farm name</span>
              <input className="input" {...farmForm.register("name")} />
              {farmForm.formState.errors.name && (
                <span className="error">
                  {farmForm.formState.errors.name.message}
                </span>
              )}
            </label>
            <label>
              <span className="label">Responsible contact</span>
              <input className="input" {...farmForm.register("contact_name")} />
            </label>
            <label>
              <span className="label">Province</span>
              <input
                className="input"
                list="provinces"
                {...farmForm.register("province")}
              />
              <datalist id="provinces">
                <option>Harare</option>
                <option>Manicaland</option>
                <option>Mashonaland Central</option>
                <option>Mashonaland East</option>
                <option>Mashonaland West</option>
                <option>Masvingo</option>
                <option>Matabeleland North</option>
                <option>Matabeleland South</option>
                <option>Midlands</option>
              </datalist>
              {farmForm.formState.errors.province && (
                <span className="error">
                  {farmForm.formState.errors.province.message}
                </span>
              )}
            </label>
            <label>
              <span className="label">District</span>
              <input className="input" {...farmForm.register("district")} />
              {farmForm.formState.errors.district && (
                <span className="error">
                  {farmForm.formState.errors.district.message}
                </span>
              )}
            </label>
            <label>
              <span className="label">Ward</span>
              <input className="input" {...farmForm.register("ward")} />
            </label>
            <div />
          </div>
          <details>
            <summary className="cursor-pointer font-bold text-ink">
              Optional location and notes
            </summary>
            <div className="mt-3 grid gap-4 sm:grid-cols-2">
              <label>
                <span className="label">Latitude</span>
                <input
                  className="input"
                  type="number"
                  step="any"
                  {...farmForm.register("latitude")}
                />
              </label>
              <label>
                <span className="label">Longitude</span>
                <input
                  className="input"
                  type="number"
                  step="any"
                  {...farmForm.register("longitude")}
                />
              </label>
              <label className="sm:col-span-2">
                <span className="label">Notes</span>
                <textarea
                  className="input min-h-24"
                  {...farmForm.register("notes")}
                />
              </label>
            </div>
          </details>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setFarmOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createFarm.isPending}>
              Save farm
            </Button>
          </div>
        </form>
      </Modal>

      <Modal
        open={fieldOpen}
        title="Add a maize field"
        onClose={() => setFieldOpen(false)}
      >
        <form
          className="grid gap-4"
          onSubmit={fieldForm.handleSubmit(saveField)}
        >
          <label>
            <span className="label">Farm</span>
            <select className="input" {...fieldForm.register("farm_id")}>
              <option value="">Choose a farm</option>
              {farms.data?.map((farm) => (
                <option key={farm.id} value={farm.id}>
                  {farm.name}
                </option>
              ))}
            </select>
            {fieldForm.formState.errors.farm_id && (
              <span className="error">
                {fieldForm.formState.errors.farm_id.message}
              </span>
            )}
          </label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label>
              <span className="label">Field name or number</span>
              <input className="input" {...fieldForm.register("name")} />
            </label>
            <label>
              <span className="label">Size (ha)</span>
              <input
                className="input"
                type="number"
                step="0.1"
                {...fieldForm.register("size_hectares")}
              />
            </label>
            <label>
              <span className="label">Maize variety</span>
              <input
                className="input"
                {...fieldForm.register("maize_variety")}
              />
            </label>
            <label>
              <span className="label">Planting date</span>
              <input
                className="input"
                type="date"
                {...fieldForm.register("planting_date")}
              />
            </label>
            <label>
              <span className="label">Season</span>
              <input className="input" {...fieldForm.register("season")} />
            </label>
            <label>
              <span className="label">Target yield (t/ha)</span>
              <input
                className="input"
                type="number"
                step="0.1"
                {...fieldForm.register("target_yield_t_ha")}
              />
            </label>
          </div>
          <label>
            <span className="label">Notes</span>
            <textarea
              className="input min-h-20"
              {...fieldForm.register("notes")}
            />
          </label>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setFieldOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createField.isPending}>
              Save field
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
