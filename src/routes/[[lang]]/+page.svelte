<script lang="ts">
  import type { PageData } from './$types';
  import { lekhAH, viewCountData, mode, counted } from '@state/main';
  import { fetch_post } from '@tools/fetch';
  import { onMount } from 'svelte';
  import { API_URL } from '@components/main/type';
  import LangMetaTags from '@components/tags/LangMetaTags.svelte';
  import Footer from '@components/main/Footer.svelte';
  import LoginPage from '@components/main/Login/Login.svelte';
  import SubmitData from '@components/main/Login/SubmitData.svelte';
  import { mode as modeLoginPage } from '@components/main/Login/store';
  import Result from '@components/main/Result.svelte';

  export let data: PageData;

  $: $lekhAH = data.lekh;

  $: lekh = $lekhAH;

  onMount(async () => {
    if (import.meta.env.DEV) return;
    let update_count = true;
    if (sessionStorage.getItem('page_counted') === 'true') {
      update_count = false;
    }
    const req = await fetch_post(API_URL + `/api/page_view_count?update_count=${update_count}`);
    if (!req.ok) return;
    const {
      page_view_count,
      result_view_count
    }: {
      page_view_count: number;
      result_view_count: number;
    } = await req.json();
    $viewCountData = [page_view_count, result_view_count];
    sessionStorage.setItem('page_counted', 'true');
    $counted = true;
  });
</script>

<LangMetaTags title={lekh.title} description={lekh.description} />
<svelte:head>
  <title>{lekh.title}</title>
</svelte:head>
<div class="flex h-full w-full flex-col justify-between overflow-y-scroll bg-orange-50">
  <div class="p-2">
    <h1 class="text-center text-2xl font-bold">
      <span class="bg-gradient-to-r from-red-600 to-blue-800 bg-clip-text text-transparent"
        >{lekh.title}</span
      >
    </h1>
    <div>
      {#if $mode === 'main'}
        <div class="my-4">
          {#if $modeLoginPage === 'login'}
            <LoginPage />
          {:else if $modeLoginPage === 'submit_data'}
            <SubmitData />
          {/if}
        </div>
      {:else if $mode === 'result'}
        <Result />
      {/if}
    </div>
  </div>
  <Footer />
</div>
